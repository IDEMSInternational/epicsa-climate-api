from os import path
import os

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_status():
    response = client.get("/v2/status/")
    assert response.status_code == 200
    assert "Server Up (/v2)" in response.text
