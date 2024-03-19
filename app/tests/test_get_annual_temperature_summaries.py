import json
import os

import pytest
from fastapi.testclient import TestClient
from app.main import app

pytestmark = pytest.mark.skip()
client = TestClient(app)


def assert_result_structure(result):
    assert "metadata" in result
    assert "data" in result

def assert_mean_tmin(metadata):
    assert "mean_tmin" in metadata
    assert "to" in metadata["mean_tmin"]
    assert "na_rm" in metadata["mean_tmin"]

def assert_mean_tmax(metadata):
    assert "mean_tmax" in metadata
    assert "to" in metadata["mean_tmax"]
    assert "na_rm" in metadata["mean_tmax"]

def assert_first_data_entry_structure_mean_tmin(first_data_entry):
    assert "year" in first_data_entry
    assert "station_name" in first_data_entry
    assert "mean_tmin" in first_data_entry

def assert_first_data_entry_structure_mean_tmax(first_data_entry):
    assert "year" in first_data_entry
    assert "station_name" in first_data_entry
    assert "mean_tmax" in first_data_entry

def test_get_annual_temperature_summaries_structure_zm_test_1():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "mean_tmin",
            "mean_tmax"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_temperature_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_mean_tmin(result["metadata"])
    assert_mean_tmax(result["metadata"])
   
    assert_first_data_entry_structure_mean_tmin(result["data"][0])
    assert_first_data_entry_structure_mean_tmax(result["data"][0])


def test_get_annual_temperature_summaries_data_zm_test_1():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "mean_tmin",
            "mean_tmax"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_temperature_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200


    test_folder = os.path.dirname(os.path.abspath(__file__))
    results_folder = os.path.join(test_folder, "results")
    expected_result_path = os.path.join(results_folder, "annual_temperature_summaries_test_1.json")
    # Read the expected result from a file
    with open(expected_result_path, "r") as file:
        expected_result = json.load(file)

    # Compare the response with the expected result
    assert response.json() == expected_result

def test_get_annual_temperature_summaries_structure_zm_test_1_mean_tmax_only():
        # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "mean_tmax"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_temperature_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_mean_tmax(result["metadata"])
   
    assert_first_data_entry_structure_mean_tmax(result["data"][0])

def test_get_annual_temperature_summaries_structure_zm_test_1_mean_tmin_only():
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

    result = response.json()

    assert_result_structure(result)

    assert_mean_tmin(result["metadata"])
   
    assert_first_data_entry_structure_mean_tmin(result["data"][0])
  
def test_get_annual_temperature_summaries_structure_zm_01122():
    test_data = {
        "country": "zm",
        "station_id": "01122",
        "summaries": [
            "mean_tmin",
            "mean_tmax"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_temperature_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200
    
    result = response.json()

    assert_result_structure(result)

    assert_mean_tmin(result["metadata"])
    assert_mean_tmax(result["metadata"])
   
    assert_first_data_entry_structure_mean_tmin(result["data"][0])
    assert_first_data_entry_structure_mean_tmax(result["data"][0])
