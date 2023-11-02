from fastapi.testclient import TestClient


def test_read_status(client: TestClient):
    response = client.get("/v1/status")
    assert response.status_code == 200
    assert response.json() == []
