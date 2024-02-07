import json
import os
from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)


def assert_result_structure(result):
    assert "metadata" in result
    assert "data" in result

def assert_metadata_structure(metadata):
    assert "extremes_rain" in metadata
    assert "type" in metadata["extremes_rain"]
    assert "value" in metadata["extremes_rain"]

def assert_first_data_entry_structure(first_data_entry):
    assert "station" in first_data_entry
    assert "date" in first_data_entry
    assert "year" in first_data_entry
    assert  "month" in first_data_entry
    assert "doy" in first_data_entry
    assert "day" in first_data_entry
    assert "tmax" in first_data_entry
    assert "tmin" in first_data_entry
    assert "rain" in first_data_entry

def test_get_extremes_summaries_structure_zm_test_1():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "extremes_rain",
            "extremes_tmin",
            "extremes_tmax"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/extremes_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)
    assert_metadata_structure(result["metadata"])   
    assert_first_data_entry_structure(result["data"][0])

def test_get_extremes_summaries_data_zm_test_1():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "extremes_rain",
            "extremes_tmin",
            "extremes_tmax"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/extremes_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200


    test_folder = os.path.dirname(os.path.abspath(__file__))
    results_folder = os.path.join(test_folder, "results")
    expected_result_path = os.path.join(results_folder, "extremes_summaries_test_1.json")
    # Read the expected result from a file
    with open(expected_result_path, "r") as file:
        expected_result = json.load(file)

    # Compare the response with the expected result
    assert response.json() == expected_result

def test_get_extremes_summaries_structure_zm_test_1_extremes_rain_only():
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "extremes_rain"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/extremes_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()
    assert_result_structure(result)
    assert_metadata_structure(result["metadata"])   
    assert_first_data_entry_structure(result["data"][0])

def test_get_extremes_summaries_structure_zm_test_1_extremes_tmin_only():
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "extremes_tmin"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/extremes_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()
    assert_result_structure(result)
    assert_metadata_structure(result["metadata"])   
    assert_first_data_entry_structure(result["data"][0])

def test_get_extremes_summaries_structure_zm_test_1_extremes_tmax_only():
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "extremes_tmax"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/extremes_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()
    assert_result_structure(result)
    assert_metadata_structure(result["metadata"])   
    assert_first_data_entry_structure(result["data"][0])

