from fastapi.testclient import TestClient

from app.api.v1.endpoints.select_query import router as select_router
from app.main import app


client = TestClient(app)


def test_select_query_success(monkeypatch):
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        select_router,
        "_load_db_secret",
        lambda _: {
            "host": "localhost",
            "port": 5432,
            "dbname": "example",
            "user": "example",
            "password": "example",
        },
    )

    def fake_execute_select_query(sql, params, secret):
        captured["sql"] = sql
        captured["params"] = params
        return ["station_id", "time_value"], [{"station_id": "dodoma", "time_value": "2024"}]

    monkeypatch.setattr(
        select_router,
        "execute_select_query",
        fake_execute_select_query,
    )

    response = client.post(
        "/v1/select_query/",
        json={
            "table_name": "summary",
            "columns": ["station_id", "time_value"],
            "station_id": "dodoma",
            "order_by": "time_value",
            "order_direction": "desc",
            "max_rows": 10,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["columns"] == ["station_id", "time_value"]
    assert body["row_count"] == 1
    assert body["rows"] == [{"station_id": "dodoma", "time_value": "2024"}]
    assert "from summary" in str(captured["sql"]).lower()
    assert captured["params"] == ["dodoma", 10]


def test_select_query_rejects_invalid_column():
    response = client.post(
        "/v1/select_query/",
        json={
            "table_name": "summary",
            "columns": ["station_id", "invalid_column"],
            "station_id": "dodoma",
            "max_rows": 10,
        },
    )

    assert response.status_code == 400
    assert "Unsupported columns" in response.json()["detail"]


def test_select_query_rejects_invalid_order_by():
    response = client.post(
        "/v1/select_query/",
        json={
            "table_name": "station",
            "station_id": "dodoma",
            "order_by": "time_value",
            "max_rows": 10,
        },
    )

    assert response.status_code == 400
    assert "Unsupported order_by" in response.json()["detail"]


def test_select_query_rejects_unknown_table_name():
    response = client.post(
        "/v1/select_query/",
        json={
            "table_name": "unknown_table",
            "station_id": "dodoma",
            "max_rows": 10,
        },
    )

    assert response.status_code == 422

def test_select_query_missing_secret_file(monkeypatch):
    class FakeSettings:
        POSTGRES_SECRET_FILE = "./does-not-exist.json"

    monkeypatch.setattr(select_router, "Settings", lambda: FakeSettings())

    response = client.post(
        "/v1/select_query/",
        json={
            "table_name": "summary",
            "station_id": "dodoma",
            "max_rows": 10,
        },
    )

    assert response.status_code == 500
    assert "Postgres secret file not found" in response.json()["detail"]
