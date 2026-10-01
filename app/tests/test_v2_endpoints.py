import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Configure test database:
# 1. Use existing EPICSA_SQLITE_DB if already set and valid
# 2. Check for local snapshot: data_snapshot/epicsa_local.db
# 3. Fall back to creating a temporary SQLite db from app/tests/data/test_epicsa.sql
if not os.environ.get("EPICSA_SQLITE_DB") or not Path(os.environ["EPICSA_SQLITE_DB"]).exists():
    snapshot_db = Path("data_snapshot/epicsa_local.db").resolve()
    sql_fixture = Path(__file__).parent / "data" / "test_epicsa.sql"
    if snapshot_db.exists():
        os.environ["EPICSA_SQLITE_DB"] = str(snapshot_db)
    elif sql_fixture.exists():
        import sqlite3
        import tempfile

        tmp_db = Path(tempfile.gettempdir()) / "epicsa_test_fixture.db"
        if not tmp_db.exists() or tmp_db.stat().st_size == 0:
            conn = sqlite3.connect(tmp_db)
            conn.executescript(sql_fixture.read_text(encoding="utf-8"))
            conn.close()
        os.environ["EPICSA_SQLITE_DB"] = str(tmp_db)

from app.main import app

client = TestClient(app)


def test_v2_status():
    """Verify v2 health check endpoint."""
    response = client.get("/v2/status/")
    assert response.status_code == 200
    assert "Server Up (/v2)" in response.text


def test_v2_station_list():
    """Verify listing stations for country 'zm' and 'zw'."""
    # Zambia
    res_zm = client.get("/v2/station/zm")
    assert res_zm.status_code == 200
    data_zm = res_zm.json()["data"]
    assert len(data_zm) > 0
    assert any("CHOMA" in s["station_id"] for s in data_zm)

    # Zimbabwe
    res_zw = client.get("/v2/station/zw")
    assert res_zw.status_code == 200
    data_zw = res_zw.json()["data"]
    assert len(data_zw) > 0
    assert any("BEITBRIDGE" in s["station_id"] for s in data_zw)


def test_v2_station_detail():
    """Verify station details and climate definitions."""
    res = client.get("/v2/station/zw/BEITBRIDGE (MET)")
    assert res.status_code == 200
    body = res.json()
    assert body["station_id"] == "BEITBRIDGE (MET)"
    assert "country_code" in body
    assert "data" in body
    assert isinstance(body["definitions_id"], list)


def test_v2_station_detail_not_found():
    """Verify 404 returned for unknown station."""
    res = client.get("/v2/station/zm/NON_EXISTENT_STATION_XYZ")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_v2_annual_rainfall_summaries():
    """Verify annual rainfall summaries endpoint."""
    payload = {
        "country": "zw",
        "station_id": "BEITBRIDGE (MET)",
    }
    res = client.post("/v2/annual_rainfall_summaries/", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "metadata" in body
    assert "data" in body
    assert len(body["data"]) > 0

    first_row = body["data"][0]
    assert "year" in first_row
    assert "station" in first_row
    assert first_row["station"] == "BEITBRIDGE (MET)"


def test_v2_annual_temperature_summaries():
    """Verify annual temperature summaries endpoint."""
    payload = {
        "country": "zw",
        "station_id": "BEITBRIDGE (MET)",
    }
    res = client.post("/v2/annual_temperature_summaries/", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "metadata" in body
    assert "data" in body
    assert len(body["data"]) > 0

    # Verify a year with known temperature data
    row_1952 = next((r for r in body["data"] if r["year"] == 1952), None)
    assert row_1952 is not None
    assert row_1952["max_tmax"] == 43.0
    assert row_1952["min_tmin"] == 4.4


def test_v2_monthly_temperature_summaries():
    """Verify monthly temperature summaries endpoint."""
    payload = {
        "country": "zw",
        "station_id": "BEITBRIDGE (MET)",
    }
    res = client.post("/v2/monthly_temperature_summaries/", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "metadata" in body
    assert "data" in body
    assert len(body["data"]) > 0

    first_row = body["data"][0]
    assert "year" in first_row
    assert "month" in first_row
    assert 1 <= first_row["month"] <= 12


def test_v2_crop_success_probabilities():
    """Verify crop success probabilities endpoint."""
    payload = {
        "country": "zw",
        "station_id": "CHISENGU (MET)",
    }
    res = client.post("/v2/crop_success_probabilities/", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "metadata" in body
    assert "data" in body
    assert len(body["data"]) > 0

    first_row = body["data"][0]
    assert "total_rain" in first_row
    assert "plant_day" in first_row
    assert "plant_length" in first_row
    assert 0.0 <= first_row["prop_success_with_start"] <= 1.0
    assert 0.0 <= first_row["prop_success_no_start"] <= 1.0


def test_v2_season_start_probabilities():
    """Verify season start probabilities endpoint."""
    payload = {
        "country": "zw",
        "station_id": "BEITBRIDGE (MET)",
        "start_dates": [100, 120, 140, 160],
    }
    res = client.post("/v2/season_start_probabilities/", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "metadata" in body
    assert "data" in body
    assert len(body["data"]) == 4

    days = [r["day"] for r in body["data"]]
    assert days == [100, 120, 140, 160]
    for r in body["data"]:
        assert 0.0 <= r["proportion"] <= 1.0


def test_v2_select_query():
    """Verify v2 select_query endpoint."""
    payload = {
        "table_name": "station",
        "station_id": "dodoma",
        "max_rows": 5,
    }
    res = client.post("/v2/select_query/", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "rows" in body
    assert body["row_count"] >= 1
