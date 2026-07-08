from fastapi.testclient import TestClient

from app.api.v1.endpoints.select_query import router as select_router
from app.main import app


client = TestClient(app)


def test_select_query_success(monkeypatch):
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
    monkeypatch.setattr(
        select_router,
        "execute_select_query",
        lambda sql, params, max_rows, secret: (
            ["id", "name"],
            [{"id": 1, "name": "demo"}],
        ),
    )

    response = client.post(
        "/v1/select_query/",
        json={"sql": "SELECT id, name FROM demo", "params": [], "max_rows": 10},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["columns"] == ["id", "name"]
    assert body["row_count"] == 1
    assert body["rows"] == [{"id": 1, "name": "demo"}]


def test_select_query_rejects_non_select_sql():
    response = client.post(
        "/v1/select_query/",
        json={"sql": "DELETE FROM demo", "params": [], "max_rows": 10},
    )

    assert response.status_code == 400
    assert "Only SELECT SQL is allowed" in response.json()["detail"]


def test_select_query_rejects_multiple_statements():
    response = client.post(
        "/v1/select_query/",
        json={"sql": "SELECT 1; SELECT 2", "params": [], "max_rows": 10},
    )

    assert response.status_code == 400
    assert "Only SELECT SQL is allowed" in response.json()["detail"]


def test_select_query_rejects_select_into():
    response = client.post(
        "/v1/select_query/",
        json={"sql": "SELECT 1 INTO new_table", "params": [], "max_rows": 10},
    )

    assert response.status_code == 400
    assert "Only SELECT SQL is allowed" in response.json()["detail"]

def test_select_query_missing_secret_file(monkeypatch):
    class FakeSettings:
        POSTGRES_SECRET_FILE = "./does-not-exist.json"

    monkeypatch.setattr(select_router, "Settings", lambda: FakeSettings())

    response = client.post(
        "/v1/select_query/",
        json={"sql": "SELECT 1", "params": [], "max_rows": 10},
    )

    assert response.status_code == 500
    assert "Postgres secret file not found" in response.json()["detail"]
