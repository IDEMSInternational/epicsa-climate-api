from fastapi.testclient import TestClient


def test_read_stations(client: TestClient):
    response = client.get("/v1/station")
    assert response.status_code == 200
    assert response.json() == []
