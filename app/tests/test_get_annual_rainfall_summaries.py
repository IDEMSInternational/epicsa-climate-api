import json
import os
from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)


def assert_result_structure(result):
    assert "metadata" in result
    assert "data" in result

def assert_annual_rain(metadata):
    assert "annual_rain" in metadata
    assert "annual_rain" in metadata["annual_rain"]
    assert "n_rain" in metadata["annual_rain"]
    assert "na_rm" in metadata["annual_rain"]

def assert_start_rains(metadata):
    assert "start_rains" in metadata
    assert "threshold" in metadata["start_rains"]
    assert "start_day" in metadata["start_rains"]
    assert "end_day" in metadata["start_rains"]
    assert "total_rainfall" in metadata["start_rains"]
    assert "amount_rain" in metadata["start_rains"]
    assert "over_days" in metadata["start_rains"]
    assert "proportion" in metadata["start_rains"]
    assert "number_rain_days" in metadata["start_rains"]
    assert "dry_spell" in metadata["start_rains"]
    assert "spell_max_dry_days" in metadata["start_rains"]
    assert "spell_interval" in metadata["start_rains"]
    assert "dry_period" in metadata["start_rains"]
    assert "_last_updated" in metadata["start_rains"]

def assert_end_rains(metadata):
    assert "end_rains" in metadata
    assert "start_day" in metadata["end_rains"]
    assert "end_day" in metadata["end_rains"]
    assert "interval_length" in metadata["end_rains"]
    assert "min_rainfall" in metadata["end_rains"]

def assert_end_season(metadata):
    assert "end_season" in metadata
    assert "start_day" in metadata["end_season"]
    assert "end_day" in metadata["end_season"]
    assert "capacity" in metadata["end_season"]
    assert "water_balance_max" in metadata["end_season"]
    assert "evaporation" in metadata["end_season"]
    assert "evaporation_value" in metadata["end_season"]

def assert_seasonal_rain(metadata):
    assert "seasonal_rain" in metadata
    assert "seasonal_rain" in metadata["seasonal_rain"]
    assert "end_type" in metadata["seasonal_rain"]
    assert "n_rain" in metadata["seasonal_rain"]
    assert "na_rm" in metadata["seasonal_rain"]
    assert "rain_day" in metadata["seasonal_rain"]
    assert "total_rain" in metadata["seasonal_rain"]
         

def assert_seasonal_length(metadata):
    assert "seasonal_length" in metadata
    assert "end_type" in metadata["seasonal_length"]

def assert_first_data_entry_structure_annual_rain(first_data_entry):
    assert "year" in first_data_entry
    assert "station_name" in first_data_entry
    assert "annual_rain" in first_data_entry
    assert "n_rain" in first_data_entry

def assert_first_data_entry_structure_start_rains(first_data_entry):
    assert "year" in first_data_entry
    assert "station_name" in first_data_entry
    assert "start_rains" in first_data_entry

def assert_first_data_entry_structure_end_rains(first_data_entry):
    assert "year" in first_data_entry
    assert "station_name" in first_data_entry
    assert "end_rains" in first_data_entry

def assert_first_data_entry_structure_end_season(first_data_entry):
    assert "year" in first_data_entry
    assert "station_name" in first_data_entry
    assert "end_season" in first_data_entry

def assert_first_data_entry_structure_seasonal_rain(first_data_entry):
    assert "year" in first_data_entry
    assert "station_name" in first_data_entry
    assert  "seasonal_rain" in first_data_entry
    assert  "n_seasonal_rain" in first_data_entry

def assert_first_data_entry_structure_seasonal_length(first_data_entry):
    assert "year" in first_data_entry
    assert "station_name" in first_data_entry
    assert  "season_length" in first_data_entry

def test_get_annual_rainfall_summaries_structure_zm_test_1():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "annual_rain",
            "start_rains",
            "end_rains",
            "end_season",
            "seasonal_rain",
            "seasonal_length"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_annual_rain(result["metadata"])
    assert_start_rains(result["metadata"])
    assert_end_rains(result["metadata"])
    assert_end_season(result["metadata"])
    assert_seasonal_rain(result["metadata"])
    assert_seasonal_length(result["metadata"])
   
    assert_first_data_entry_structure_annual_rain(result["data"][0])
    assert_first_data_entry_structure_start_rains(result["data"][0])
    assert_first_data_entry_structure_end_rains(result["data"][0])
    assert_first_data_entry_structure_end_season(result["data"][0])
    assert_first_data_entry_structure_seasonal_rain(result["data"][0])
    assert_first_data_entry_structure_seasonal_length(result["data"][0])

def test_get_annual_rainfall_summaries_data_zm_test_1():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "annual_rain",
            "start_rains",
            "end_rains",
            "end_season",
            "seasonal_rain",
            "seasonal_length"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200


    test_folder = os.path.dirname(os.path.abspath(__file__))
    results_folder = os.path.join(test_folder, "results")
    expected_result_path = os.path.join(results_folder, "annual_rainfall_summaries_test_1.json")
    # Read the expected result from a file
    with open(expected_result_path, "r") as file:
        expected_result = json.load(file)

    # Compare the response with the expected result
    assert response.json() == expected_result

def test_get_annual_rainfall_summaries_structure_zm_01122_annual_rain_only():
        # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "01122",
        "summaries": [
            "annual_rain"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_annual_rain(result["metadata"])
   
    assert_first_data_entry_structure_annual_rain(result["data"][0])

def test_get_annual_rainfall_summaries_structure_zm_test_1_annual_rain_only():
        # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "annual_rain"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_annual_rain(result["metadata"])
   
    assert_first_data_entry_structure_annual_rain(result["data"][0])

def test_get_annual_rainfall_summaries_structure_zm_test_1_start_rains_only():
        # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "start_rains"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_start_rains(result["metadata"])
   
    assert_first_data_entry_structure_start_rains(result["data"][0])

def test_get_annual_rainfall_summaries_structure_zm_test_1_end_rains_only():
        # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "end_rains"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_end_rains(result["metadata"])
   
    assert_first_data_entry_structure_end_rains(result["data"][0])

def test_get_annual_rainfall_summaries_structure_zm_test_1_end_season_only():
        # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "end_season"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_end_season(result["metadata"])
   
    assert_first_data_entry_structure_end_season(result["data"][0])

def test_get_annual_rainfall_summaries_structure_zm_test_1_seasonal_rain_only():
        # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "seasonal_rain"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_seasonal_rain(result["metadata"])
   
    assert_first_data_entry_structure_seasonal_rain(result["data"][0])

def test_get_annual_rainfall_summaries_structure_zm_test_1_seasonal_length_only():
        # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "summaries": [
            "seasonal_length"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_seasonal_length(result["metadata"])
   
    assert_first_data_entry_structure_seasonal_length(result["data"][0])
    
def test_get_annual_rainfall_summaries_structure_zm_01122():
    test_data = {
        "country": "zm",
        "station_id": "01122",
        "summaries": [
            "annual_rain",
            "start_rains",
            "end_rains",
            "end_season",
            "seasonal_rain",
            "seasonal_length"
        ],
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)

    assert_annual_rain(result["metadata"])
    assert_start_rains(result["metadata"])
    assert_end_rains(result["metadata"])
    assert_end_season(result["metadata"])
    assert_seasonal_rain(result["metadata"])
    assert_seasonal_length(result["metadata"])
   
    assert_first_data_entry_structure_annual_rain(result["data"][0])
    assert_first_data_entry_structure_start_rains(result["data"][0])
    assert_first_data_entry_structure_end_rains(result["data"][0])
    assert_first_data_entry_structure_end_season(result["data"][0])
    assert_first_data_entry_structure_seasonal_rain(result["data"][0])
    assert_first_data_entry_structure_seasonal_length(result["data"][0])