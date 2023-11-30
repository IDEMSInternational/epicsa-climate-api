from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app instance is named 'app'

client = TestClient(app)

def assert_result_structure(result):
    assert "metadata" in result
    assert "data" in result

def assert_start_rains_structure(metadata):
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
    assert "_last_updated"in metadata["start_rains"]

def assert_end_rains_structure(metadata):
    assert "end_rains" in metadata
    assert "start_day" in metadata["end_rains"]
    assert "end_day" in metadata["end_rains"]
    assert "interval_length" in metadata["end_rains"]
    assert "min_rainfall" in metadata["end_rains"]

def assert_crops_success_structure(metadata):
    assert "crops_success" in metadata
    assert "water_requirements" in metadata["crops_success"]
    assert "planting_dates" in metadata["crops_success"]
    assert"planting_length" in metadata["crops_success"]
    assert"start_check" in metadata["crops_success"]


def test_get_crop_success_probabilities():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "16",
        "water_requirements": [0],
        "planting_length": [0],
        "planting_dates": [0],
        "start_before_season": True
    }

def assert_first_data_entry_structure(first_data_entry):
    assert "year" in first_data_entry
    assert "station_name" in first_data_entry
    assert "start_rains" in first_data_entry


    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/crop_success_probabilities/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()
    assert_result_structure(result)
   # Check the metadata
    assert_start_rains_structure(result["metadata"])
    assert_end_rains_structure(result["metadata"])
    assert_crops_success_structure(result["metadata"])

    # Check the data
    assert "data" in result
    assert len(result["data"]) == 1  # Assuming there is one entry in the data list

    # Example: Check the structure of the first data entry
    first_data_entry = result["data"][0]
    assert "station_name" in first_data_entry
    assert "water_requirements" in first_data_entry
    assert "planting_day" in first_data_entry
    assert "planting_length" in first_data_entry
    assert "prop_success" in first_data_entry

    # Add more specific assertions based on the expected output

    # Example: Check the values of the first data entry
    assert first_data_entry["station_name"] == "LUNDAZI MET"
    assert first_data_entry["water_requirements"] == 0
    assert first_data_entry["planting_day"] == 0
    assert first_data_entry["planting_length"] == 0
    assert first_data_entry["prop_success"] == 0
