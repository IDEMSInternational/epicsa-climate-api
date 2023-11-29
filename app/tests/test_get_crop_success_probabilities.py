from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app instance is named 'app'

client = TestClient(app)

def test_get_annual_rainfall_summaries():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "16",
        "water_requirements": [0],
        "planting_length": [0],
        "planting_dates": [0],
        "start_before_season": True
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/crop_success_probabilities/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

   # Check the structure of the response JSON
    result = response.json()
    assert "metadata" in result
    assert "data" in result

   # Check the metadata
    assert "start_rains" in result["metadata"]
    assert "end_rains" in result["metadata"]
    assert "crops_success" in result["metadata"]

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
