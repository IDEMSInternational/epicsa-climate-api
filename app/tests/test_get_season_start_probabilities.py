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

def assert_season_start_probabilities_structure(metadata):
    assert "season_start_probabilities" in metadata
    assert "specified_day" in metadata["season_start_probabilities"]

def assert_first_data_entry_structure(first_data_entry):
    assert "station_name" in first_data_entry
    


def test_get_season_start_probabilities_structure_zm_test_1():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "test_1",
        "start_dates": [0]
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/season_start_probabilities/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()
    assert_result_structure(result)
    # Check the metadata
    assert_start_rains_structure(result["metadata"])
    assert_season_start_probabilities_structure(result["metadata"])

    assert_first_data_entry_structure(result["data"][0])