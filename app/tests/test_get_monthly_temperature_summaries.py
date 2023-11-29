from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app instance is named 'app'

client = TestClient(app)

def test_get_monthly_temperature_summaries():
    # Define test input data
    test_data = {
        "country": "zm",
        "station_id": "16",
        "summaries": ["mean_tmin","mean_tmax"]
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/monthly_temperature_summaries/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

   # Check the structure of the response JSON
    result = response.json()
    assert "metadata" in result
    assert "data" in result

   # Check the metadata
    assert "mean_tmin" in result["metadata"]
    assert "mean_tmax" in result["metadata"]

    # Check the data
    assert "data" in result
    assert len(result["data"]) == 799  # Assuming there is one entry in the data list

    # Example: Check the structure of the first data entry
    first_data_entry = result["data"][0]
    assert "station_name" in first_data_entry
    assert "year" in first_data_entry
    assert "month" in first_data_entry
    assert "mean_tmin" in first_data_entry
    assert "mean_tmax" in first_data_entry

    # Add more specific assertions based on the expected output

    # Example: Check the values of the first data entry
    assert first_data_entry["station_name"] == "LUNDAZI MET"
    assert first_data_entry["year"] == 1956
    assert first_data_entry["month"] == 1
    assert first_data_entry["mean_tmin"] == ""
    assert first_data_entry["mean_tmax"] == ""