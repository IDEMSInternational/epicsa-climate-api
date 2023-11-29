import json
import os
from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

def test_get_annual_temperature_summaries_zm_test_1():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "mean_tmin"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_temperature_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

