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
    zw_ids = [s["station_id"] for s in data_zw]
    # Ensure numeric IDs (e.g. 67991020) are filtered out and list is unique
    assert not any(sid.isdigit() for sid in zw_ids)
    assert len(zw_ids) == len(set(zw_ids))


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
    """Verify annual rainfall summaries endpoint trims pre-commissioning null grid years."""
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

    # 1909 is an empty padding year and must be trimmed.
    # In test_epicsa.sql observations start in 1950; in full snapshot in 1922.
    years = [r["year"] for r in body["data"]]
    assert 1909 not in years
    assert years[0] in (1922, 1950)
    assert all(yr >= years[0] for yr in years)

    first_row = body["data"][0]
    assert first_row["year"] == years[0]
    assert first_row["station"] == "BEITBRIDGE (MET)"
    assert first_row["annual_rain"] is not None

    # Verify 1950 correctly separates annual rain (Oct_Apr_PRECIP) and seasonal rain (seasonal_PRECIP)
    row_1950 = next((r for r in body["data"] if r["year"] == 1950), None)
    assert row_1950 is not None
    assert row_1950["annual_rain"] == 296
    assert row_1950["seasonal_rain"] == 236
    assert row_1950["n_rain"] == 24
    assert row_1950["n_seasonal_rain"] == 14


def test_v2_annual_temperature_summaries():
    """Verify annual temperature summaries endpoint trims pre-observation null years."""
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

    # 1922..1951 are empty padding years, 1952 is first year with temperature data
    years = [r["year"] for r in body["data"]]
    assert 1922 not in years or years[0] == 1952
    assert years[0] == 1952
    assert all(yr >= 1952 for yr in years)

    # Verify a year with known temperature data
    row_1952 = next((r for r in body["data"] if r["year"] == 1952), None)
    assert row_1952 is not None
    assert row_1952["max_tmax"] == 43.0
    assert row_1952["min_tmin"] == 4.4


def test_v2_monthly_temperature_summaries():
    """Verify monthly temperature summaries endpoint trims pre-observation null months."""
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
    # Observations start in 1951 (full snapshot) or 1952 (test_epicsa.sql)
    assert first_row["year"] in (1951, 1952)
    assert 1 <= first_row["month"] <= 12
    # Verify unobserved pre-1950 months are trimmed
    assert not any(r["year"] < 1950 for r in body["data"])


def test_climate_repository_internal_trim_parameters():
    """Verify ClimateRepository methods support internal trim_start and trim_end parameters."""
    from app.services.climate_repository import get_climate_repository

    repo = get_climate_repository()

    # Annual rainfall: untrimmed starts at 1909, trimmed excludes 1909
    res_trimmed = repo.get_annual_rainfall_summaries("zw", "BEITBRIDGE (MET)", trim_start=True)
    assert 1909 not in [r.year for r in res_trimmed.data]
    assert res_trimmed.data[0].year in (1922, 1950)
    res_untrimmed = repo.get_annual_rainfall_summaries("zw", "BEITBRIDGE (MET)", trim_start=False)
    assert res_untrimmed.data[0].year == 1909

    # Annual temperature: trimmed starts at 1952
    res_temp_trimmed = repo.get_annual_temperature_summaries("zw", "BEITBRIDGE (MET)", trim_start=True)
    assert res_temp_trimmed.data[0].year == 1952

    # Monthly temperature: trimmed starts in 1951 or 1952, pre-1950 is trimmed
    res_m_trimmed = repo.get_monthly_temperature_summaries("zw", "BEITBRIDGE (MET)", trim_start=True)
    assert res_m_trimmed.data[0].year in (1951, 1952)
    assert not any(r.year < 1950 for r in res_m_trimmed.data)


def test_v2_crop_success_probabilities():
    """Verify crop success probabilities endpoint returns the full lookup table and has no extra filter options."""
    from app.api.v2.endpoints.crop_success_probabilities.schema import CropSuccessProbabilitiesParameters

    # Verify schema ONLY gives country and station_id
    assert set(CropSuccessProbabilitiesParameters.__fields__.keys()) == {"country", "station_id"}

    # Test CHISENGU (MET) returns lookup table (3 rows in test fixture, 819 in full DB)
    payload = {
        "country": "zw",
        "station_id": "CHISENGU (MET)",
    }
    res = client.post("/v2/crop_success_probabilities/", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "metadata" in body
    assert "data" in body
    assert len(body["data"]) in (3, 819)

    first_row = body["data"][0]
    assert "total_rain" in first_row
    assert "plant_day" in first_row
    assert "plant_length" in first_row
    assert 0.0 <= first_row["prop_success_with_start"] <= 1.0
    assert 0.0 <= first_row["prop_success_no_start"] <= 1.0

    # Test CHOMA MET returns precalculated lookup table (from test DB fixture)
    payload_zm = {
        "country": "zm",
        "station_id": "CHOMA MET",
    }
    res_zm = client.post("/v2/crop_success_probabilities/", json=payload_zm)
    assert res_zm.status_code == 200
    body_zm = res_zm.json()
    assert len(body_zm["data"]) >= 1
    choma_row = body_zm["data"][0]
    assert choma_row["total_rain"] == 200
    assert choma_row["plant_day"] == 123
    assert choma_row["plant_length"] == 60
    assert choma_row["prop_success_with_start"] == 0.5
    assert choma_row["prop_success_no_start"] == 0.75


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


def test_climate_repository_annual_rainfall_summaries_subseasonal_and_seasonal_mapping(monkeypatch):
    """Verify that OND_rainfall does not overwrite Annual_rainfall and that Seasonal_Rain maps correctly."""
    from app.services import climate_repository as cr_mod

    # Mock Magoye-like rows: Annual_rainfall (613.7) and OND_rainfall (123.9) both under total_rain
    magoye_rows = [
        {"time_value": "1981", "summary_element": "total_rain", "summary_name": "Annual_rainfall", "summary_value": "613.7"},
        {"time_value": "1981", "summary_element": "total_rain", "summary_name": "OND_rainfall", "summary_value": "123.9"},
        {"time_value": "1981", "summary_element": "rain_day", "summary_name": "No_of_raindays", "summary_value": "50"},
        {"time_value": "1981", "summary_element": "start_rain", "summary_name": "start", "summary_value": "173"},
        {"time_value": "1981", "summary_element": "start_rain_date", "summary_name": "start_d", "summary_value": "1981-12-20"},
        {"time_value": "1981", "summary_element": "start_rain_status", "summary_name": "start_s", "summary_value": "TRUE"},
        {"time_value": "1981", "summary_element": "end_season", "summary_name": "end_season", "summary_value": "259"},
        {"time_value": "1981", "summary_element": "end_season_date", "summary_name": "end_season_date", "summary_value": "1982-03-15"},
        {"time_value": "1981", "summary_element": "end_season_status", "summary_name": "end_season_status", "summary_value": "TRUE"},
        {"time_value": "1981", "summary_element": "season_length", "summary_name": "length", "summary_value": "86"},
    ]

    def mock_execute_query(sql, params=None):
        if "FROM summary_station_metadata" in sql:
            return [], []
        if "FROM summary" in sql:
            return [], magoye_rows
        return [], []

    monkeypatch.setattr(cr_mod, "execute_query", mock_execute_query)
    repo = cr_mod.ClimateRepository()
    res = repo.get_annual_rainfall_summaries("zm", "MAGOYE AGROMET", trim_start=False, trim_end=False)
    assert len(res.data) == 1
    row = res.data[0]
    assert row.year == 1981
    assert row.annual_rain == 614  # NOT 123.9
    assert row.seasonal_rain is None
    assert row.n_rain == 50
    assert row.season_length == 86.0
    assert row.end_season_doy == 259

    # Mock Chinsali-like rows: Seasonal_Rain (577.2) and Seasonal_Raindays (33)
    chinsali_rows = [
        {"time_value": "2016", "summary_element": "total_rain", "summary_name": "Annual_Rain", "summary_value": "577.2"},
        {"time_value": "2016", "summary_element": "total_rain", "summary_name": "Seasonal_Rain", "summary_value": "577.2"},
        {"time_value": "2016", "summary_element": "total_rain", "summary_name": "OND_rainfall", "summary_value": "318.7"},
        {"time_value": "2016", "summary_element": "rain_day", "summary_name": "Annual_Raindays", "summary_value": "33"},
        {"time_value": "2016", "summary_element": "rain_day", "summary_name": "Seasonal_Raindays", "summary_value": "33"},
        {"time_value": "2016", "summary_element": "season_length", "summary_name": "length", "summary_value": "89"},
    ]

    monkeypatch.setattr(cr_mod, "execute_query", lambda sql, params=None: ([], [] if "metadata" in sql else chinsali_rows))
    res_ch = repo.get_annual_rainfall_summaries("zm", "CHINSALI FTC", trim_start=False, trim_end=False)
    assert len(res_ch.data) == 1
    row_ch = res_ch.data[0]
    assert row_ch.annual_rain == 577
    assert row_ch.seasonal_rain == 577
    assert row_ch.n_rain == 33
    assert row_ch.n_seasonal_rain == 33


def test_variable_mappings_exact_matches():
    from app.services.variable_mappings import map_annual_rain_field

    # Exact annual rainfall metrics (rounded to nearest mm)
    assert map_annual_rain_field("total_rain", "Annual_Rain", "613.7") == ("annual_rain", 614)
    assert map_annual_rain_field("total_rain", "annual_rain", "613.7") == ("annual_rain", 614)
    assert map_annual_rain_field("total_rain", "total_rain", "613.7") == ("annual_rain", 614)
    assert map_annual_rain_field("total_rain", "Annual_rainfall", "613.7") == ("annual_rain", 614)

    # Exact seasonal rainfall metrics (rounded to nearest mm)
    assert map_annual_rain_field("total_rain", "Seasonal_Rain", "577.2") == ("seasonal_rain", 577)
    assert map_annual_rain_field("seasonal_rain", "seasonal_rain", "577.2") == ("seasonal_rain", 577)
    assert map_annual_rain_field("seasonal_precip", "seasonal_precip", "577.2") == ("seasonal_rain", 577)

    # Rain day counts
    assert map_annual_rain_field("rain_day", "Annual_Raindays", "50") == ("n_rain", 50)
    assert map_annual_rain_field("rain_day", "No_of_raindays", "50") == ("n_rain", 50)
    assert map_annual_rain_field("rain_day", "Seasonal_Raindays", "33") == ("n_seasonal_rain", 33)

    # Dates and statuses
    assert map_annual_rain_field("start_rain", "start", "173") == ("start_rains_doy", 173)
    assert map_annual_rain_field("start_rain_date", "start_d", "1981-12-20") == ("start_rains_date", "1981-12-20")
    assert map_annual_rain_field("start_rain_status", "start_s", "TRUE") == ("start_rains_status", True)
    assert map_annual_rain_field("end_season", "end_season", "259") == ("end_season_doy", 259)
    assert map_annual_rain_field("end_season_date", "end_season_date", "1982-03-15") == ("end_season_date", "1982-03-15")
    assert map_annual_rain_field("end_season_status", "end_season_status", "FALSE") == ("end_season_status", False)
    assert map_annual_rain_field("season_length", "length", "86") == ("season_length", 86.0)


def test_variable_mappings_subseasonal_and_auxiliary_exclusion():
    from app.services.variable_mappings import map_annual_rain_field

    # 3-month sub-seasonal blocks must never map to annual_rain
    assert map_annual_rain_field("total_rain", "OND_rainfall", "123.9") is None
    assert map_annual_rain_field("total_rain", "djf_rainfall", "200.0") is None
    assert map_annual_rain_field("total_rain", "mam_rainfall", "150.0") is None
    assert map_annual_rain_field("total_rain", "jja_rainfall", "10.0") is None
    assert map_annual_rain_field("total_rain", "son_rainfall", "50.0") is None

    # Dry spells must not map to annual_rain
    assert map_annual_rain_field("total_rain", "max_dry_spell", "15") is None
    assert map_annual_rain_field("total_rain", "longest_dry_spell", "20") is None

    # Start of rains with dry spell criteria must not map to standard start of rains
    assert map_annual_rain_field("start_rain", "start_dry", "180") is None
    assert map_annual_rain_field("start_rain", "start_dryspell", "180") is None
    assert map_annual_rain_field("start_rain", "dryspell", "180") is None
    assert map_annual_rain_field("start_rain_date", "start_dry_d", "1981-12-20") is None
    assert map_annual_rain_field("start_rain_date", "star_dry_d", "1981-12-20") is None
    assert map_annual_rain_field("start_rain_date", "start_d_dryspell", "1981-12-20") is None
    assert map_annual_rain_field("start_rain_date", "dryspell_d", "1981-12-20") is None
    assert map_annual_rain_field("start_rain_status", "start_dry_s", "TRUE") is None
    assert map_annual_rain_field("start_rain_status", "start_s_dryspell", "TRUE") is None
    assert map_annual_rain_field("start_rain_status", "dryspell_s", "1") is None


def test_variable_mappings_safe_converters():
    from app.services.variable_mappings import (
        _safe_float,
        _safe_round,
        _safe_int,
        _safe_bool,
        _safe_str,
    )

    # Float converter
    assert _safe_float("123.45") == 123.45
    assert _safe_float("123") == 123.0
    assert _safe_float(None) is None
    assert _safe_float("") is None
    assert _safe_float("NA") is None
    assert _safe_float("invalid") is None

    # Round converter (nearest integer mm)
    assert _safe_round("123.45") == 123
    assert _safe_round("123.6") == 124
    assert _safe_round("123") == 123
    assert _safe_round(123.7) == 124
    assert _safe_round(None) is None
    assert _safe_round("") is None
    assert _safe_round("NA") is None
    assert _safe_round("invalid") is None

    # Int converter
    assert _safe_int("42") == 42
    assert _safe_int("42.0") == 42
    assert _safe_int("42.8") == 42
    assert _safe_int(None) is None
    assert _safe_int("") is None
    assert _safe_int("NA") is None

    # Bool converter
    assert _safe_bool("TRUE") is True
    assert _safe_bool("true") is True
    assert _safe_bool("t") is True
    assert _safe_bool("1") is True
    assert _safe_bool(True) is True
    assert _safe_bool("FALSE") is False
    assert _safe_bool("false") is False
    assert _safe_bool("0") is False
    assert _safe_bool(None) is None
    assert _safe_bool("NA") is None

    # Str converter
    assert _safe_str("1981-12-20") == "1981-12-20"
    assert _safe_str(None) is None
    assert _safe_str("NA") is None
    assert _safe_str("null") is None
    assert _safe_str("") is None


def test_audit_variables_logic(monkeypatch):
    from app.scripts import audit_variables as audit_mod

    mock_rows = [
        {"summary_type": "Annual Rain", "summary_element": "total_rain", "summary_name": "Annual_Rain", "row_count": 50, "station_count": 1},
        {"summary_type": "Annual Rain", "summary_element": "total_rain", "summary_name": "OND_rainfall", "row_count": 50, "station_count": 1},
        {"summary_type": "Annual Rain", "summary_element": "unknown_elem", "summary_name": "mystery_var", "row_count": 10, "station_count": 1},
        {"summary_type": "Annual Temperature", "summary_element": "tmax_max", "summary_name": "max_tmax", "row_count": 30, "station_count": 1},
        {"summary_type": "Crop", "summary_element": "plant_date", "summary_name": "plant", "row_count": 100, "station_count": 1},
    ]

    monkeypatch.setattr(audit_mod, "execute_query", lambda sql, params=None: ([], mock_rows))

    report = audit_mod.audit_summary_variables()
    assert report["summary"]["total_pairs"] == 5
    assert report["summary"]["total_rows"] == 240
    assert report["summary"]["mapped_pairs"] == 2  # Annual_Rain, tmax_max
    assert report["summary"]["auxiliary_pairs"] == 2  # OND_rainfall, Crop
    assert report["summary"]["unmapped_pairs"] == 1  # mystery_var

    unmapped = report["unmapped"][0]
    assert unmapped["summary_element"] == "unknown_elem"
    assert unmapped["summary_name"] == "mystery_var"


def test_audit_stations_logic(monkeypatch):
    from app.scripts import audit_stations as st_audit_mod

    def mock_execute_query(sql, params=None):
        if "WITH annual_stations AS" in sql:
            # 5. Seasonal gaps
            return [], [
                {"station_id": "MAGOYE AGROMET", "station_name": "MAGOYE AGROMET", "country_code": "zm"}
            ]
        if "GROUP BY station_id, station_name, country_code" in sql:
            # 1. Duplicates
            return [], [
                {"station_id": "CHIPAT01", "station_name": "CHIPATA MET", "country_code": "zm", "count": 6},
                {"station_id": "67991020", "station_name": "BEITBRIDGE (MET)", "country_code": "zim", "count": 2},
            ]
        if "WHERE country_code IS NULL OR country_code NOT IN" in sql:
            # 2. Inconsistent countries
            return [], [
                {"station_id": "CHIPAT01", "station_name": "CHIPATA MET", "country_code": None},
                {"station_id": "BEITBRIDGE (MET)", "station_name": "BEITBRIDGE (MET)", "country_code": "zim"},
            ]
        if "SELECT DISTINCT station_id, station_name, country_code" in sql:
            # 3. All stations for dual-identity
            return [], [
                {"station_id": "BEITBRIDGE (MET)", "station_name": "BEITBRIDGE (MET)", "country_code": "zim"},
                {"station_id": "67991020", "station_name": "BEITBRIDGE (MET)", "country_code": "zim"},
                {"station_id": "CHIPATA MET", "station_name": "CHIPATA MET", "country_code": "zm"},
                {"station_id": "CHIPAT01", "station_name": "CHIPATA MET", "country_code": "zm"},
            ]
        if "GROUP BY station_id, summary_type" in sql:
            # 4. Multi-batch
            return [], [
                {"station_id": "BEITBRIDGE (MET)", "summary_type": "Annual Rain", "batch_count": 26, "row_count": 48222}
            ]
        return [], []

    monkeypatch.setattr(st_audit_mod, "execute_query", mock_execute_query)
    results = st_audit_mod.audit_station_integrity()
    assert results["summary"]["duplicate_row_groups"] == 2
    assert results["summary"]["inconsistent_country_codes"] == 2
    assert results["summary"]["dual_identity_stations"] == 2
    assert results["summary"]["multi_batch_stations"] == 1
    assert results["summary"]["stations_missing_seasonal_rain"] == 1

    # Verify Beitbridge dual identity
    beitbridge = next(s for s in results["dual_identity_stations"] if "BEITBRIDGE" in s["station_name"])
    assert "BEITBRIDGE (MET)" in beitbridge["text_ids"]
    assert "67991020" in beitbridge["numeric_ids"]


def test_v2_endpoints_return_generation_metadata():
    """Verify v2 endpoints return generation_id and generation_timestamp."""
    # 1. Annual rainfall summaries
    res_rain = client.post("/v2/annual_rainfall_summaries/", json={"country": "zw", "station_id": "BEITBRIDGE (MET)"})
    assert res_rain.status_code == 200
    body_rain = res_rain.json()
    assert body_rain["generation_id"] == "3frqkAVCFieVq3k6"
    assert body_rain["generation_timestamp"] is not None

    # 2. Annual temperature summaries
    res_temp = client.post("/v2/annual_temperature_summaries/", json={"country": "zw", "station_id": "BEITBRIDGE (MET)"})
    assert res_temp.status_code == 200
    body_temp = res_temp.json()
    assert body_temp["generation_id"] == "3frqkAVCFieVq3k6"
    assert body_temp["generation_timestamp"] is not None

    # 3. Monthly temperature summaries
    res_mtemp = client.post("/v2/monthly_temperature_summaries/", json={"country": "zw", "station_id": "BEITBRIDGE (MET)"})
    assert res_mtemp.status_code == 200
    body_mtemp = res_mtemp.json()
    assert body_mtemp["generation_id"] == "3frqkAVCFieVq3k6"
    assert body_mtemp["generation_timestamp"] is not None

    # 4. Crop success probabilities
    res_crop = client.post("/v2/crop_success_probabilities/", json={"country": "zw", "station_id": "CHISENGU (MET)"})
    assert res_crop.status_code == 200
    body_crop = res_crop.json()
    assert body_crop["generation_id"] in ("3frqkAVCFieVq3k6", "7VcX2GcBlQiXHyQ0")
    assert body_crop["generation_timestamp"] is not None

    # 5. Station detail
    res_stn = client.get("/v2/station/zw/BEITBRIDGE (MET)")
    assert res_stn.status_code == 200
    body_stn = res_stn.json()
    assert body_stn["generation_id"] is not None
    assert body_stn["generation_timestamp"] is not None

    # 7. Station list
    res_list = client.get("/v2/station/zw")
    assert res_list.status_code == 200
    body_list = res_list.json()
    assert len(body_list["data"]) > 0
    assert any(s["generation_timestamp"] is not None for s in body_list["data"])

    # 8. Select query
    res_query = client.post("/v2/select_query/", json={
        "table_name": "summary",
        "station_id": "BEITBRIDGE (MET)",
        "order_by": "time_stamp",
        "order_direction": "desc",
        "max_rows": 5,
    })
    assert res_query.status_code == 200
    body_query = res_query.json()
    assert body_query["generation_id"] is not None
    assert body_query["generation_timestamp"] is not None


def test_climate_repository_specific_generation_id():
    """Verify repository methods support querying a specific generation ID."""
    from app.services.climate_repository import get_climate_repository

    repo = get_climate_repository()
    # Query with specific older generation 'f2b01PJKbeIhm9z2'
    res = repo.get_annual_rainfall_summaries(
        country="zw",
        station_id="BEITBRIDGE (MET)",
        generation_id="f2b01PJKbeIhm9z2",
    )
    assert res.generation_id == "f2b01PJKbeIhm9z2"
    assert res.generation_timestamp is not None


def test_v2_manifest_country_full():
    """Verify GET /v2/manifest/{country} returns complete country inventory."""
    res = client.get("/v2/manifest/zw")
    assert res.status_code == 200
    body = res.json()
    assert body["country_code"] == "zw"
    assert body["has_updates"] is True
    assert body["latest_timestamp"] is not None
    assert body["station_count"] > 0
    assert len(body["stations"]) == body["station_count"]

    # Verify structure of first station
    stn = next((s for s in body["stations"] if s["station_id"] == "BEITBRIDGE (MET)"), None)
    assert stn is not None
    assert stn["has_updates"] is True
    assert stn["latest_timestamp"] is not None
    assert "annual_rain" in stn["generations"]
    assert "annual_temperature" in stn["generations"]
    assert "monthly_temperature" in stn["generations"]
    assert "crops" in stn["generations"]
    assert "season_start_probabilities" in stn["generations"]

    ar = stn["generations"]["annual_rain"]
    assert ar["available"] is True
    assert ar["status"] == "update_available"
    assert ar["generation_id"] is not None
    assert ar["generation_timestamp"] is not None


def test_v2_manifest_station_filter():
    """Verify station_id query parameter filters manifest to single station."""
    res = client.get("/v2/manifest/zw?station_id=BEITBRIDGE (MET)")
    assert res.status_code == 200
    body = res.json()
    assert body["station_count"] == 1
    assert len(body["stations"]) == 1
    assert body["stations"][0]["station_id"] == "BEITBRIDGE (MET)"


def test_v2_manifest_station_not_found():
    """Verify 404 is returned when station_id does not exist."""
    res = client.get("/v2/manifest/zw?station_id=NON_EXISTENT_STATION")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_v2_manifest_since_timestamp_up_to_date():
    """Verify since_timestamp matching or exceeding latest returns empty station list and has_updates=False."""
    # First get the latest timestamp
    res_initial = client.get("/v2/manifest/zw")
    assert res_initial.status_code == 200
    latest_ts = res_initial.json()["latest_timestamp"]
    assert latest_ts is not None

    # Call with since_timestamp = latest_ts
    res_check = client.get(f"/v2/manifest/zw?since_timestamp={latest_ts}")
    assert res_check.status_code == 200
    body_check = res_check.json()
    assert body_check["has_updates"] is False
    assert body_check["station_count"] == 0
    assert body_check["stations"] == []


def test_v2_manifest_since_timestamp_include_up_to_date():
    """Verify include_up_to_date=True populates all stations with 'up_to_date' status."""
    res_initial = client.get("/v2/manifest/zw")
    latest_ts = res_initial.json()["latest_timestamp"]

    res_check = client.get(f"/v2/manifest/zw?since_timestamp={latest_ts}&include_up_to_date=true")
    assert res_check.status_code == 200
    body_check = res_check.json()
    assert body_check["has_updates"] is False
    assert body_check["station_count"] > 0
    assert len(body_check["stations"]) == body_check["station_count"]

    for stn in body_check["stations"]:
        assert stn["has_updates"] is False
        for gen in stn["generations"].values():
            if gen["available"]:
                assert gen["status"] == "up_to_date"


def test_v2_manifest_since_generation_id():
    """Verify since_generation_id resolves generation and detects up-to-date vs newer data."""
    # Up-to-date case: client has latest generation 3frqkAVCFieVq3k6
    res_latest = client.get("/v2/manifest/zw?since_generation_id=3frqkAVCFieVq3k6")
    assert res_latest.status_code == 200
    body_latest = res_latest.json()
    assert body_latest["has_updates"] is False
    assert body_latest["station_count"] == 0

    # Updates available case: client has older generation f2b01PJKbeIhm9z2
    res_older = client.get("/v2/manifest/zw?since_generation_id=f2b01PJKbeIhm9z2")
    assert res_older.status_code == 200
    body_older = res_older.json()
    assert body_older["has_updates"] is True
    assert body_older["station_count"] > 0
    stn = next((s for s in body_older["stations"] if s["station_id"] == "BEITBRIDGE (MET)"), None)
    assert stn is not None
    assert stn["has_updates"] is True
    assert stn["generations"]["annual_rain"]["status"] == "update_available"




