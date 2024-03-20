from os import path
import os

import pytest
from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app instance is named 'app'

client = TestClient(app)

def test_get_status():

    # Make a request to the endpoint using the TestClient
    response = client.get("/v1/status/")

    # Check that the response has a 200 status code
    assert response.status_code == 200

    # Check the content of the response
    assert response.text == '"Server Up"'

@pytest.mark.skip()
def test_get_status_with_missing_service_account():
    # Rename or remove the service-account.json file to simulate a missing file
    # Make sure to update the path accordingly based on your project structure
    # In this example, I assume it's in the root directory
    service_account_path = "./service-account.json"
    if path.exists(service_account_path):
        # Rename the file to simulate a missing file
        os.rename(service_account_path, service_account_path + ".backup")

    try:
        # Make a request to the endpoint using the TestClient
        response = client.get("/v1/status/")  # Replace with the actual path

        # Check that the response has a 401 status code
        assert response.status_code == 401

        # Check the content of the response
        assert "service-account.json missing" in response.text
    finally:
        # Restore the original file name
        if path.exists(service_account_path + ".backup"):
            os.rename(service_account_path + ".backup", service_account_path)
