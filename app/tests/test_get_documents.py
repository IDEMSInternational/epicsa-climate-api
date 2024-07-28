import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_documents():
    test_data = {
        "prefix": "",
        "delimiter": "",
        "maxResults": 5
    }
    response = client.post("/v1/documents/", json=test_data)
    assert response.status_code == 200
