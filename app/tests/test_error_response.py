from typing import OrderedDict
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.endpoints.epicsa_data import RunEpicsaFunctionType, get_run_epicsa_function


# Define a mock implementation of the dependency
def mock_run_epicsa_function_and_get_dataframe(endpoint_function,has_dataframe = True, **kwargs):
    return OrderedDict({'metadata': OrderedDict({'wrongfield': 'wrongvalue'}),
                        'data':[{'nodata':'empty'}]})


def get_mock_run_epicsa_function() -> RunEpicsaFunctionType:
    return mock_run_epicsa_function_and_get_dataframe

client = TestClient(app)

def station_definitions_response():
    return client.get(f"/v1/station/mw_test/fake_station_id")

def annual_rainfall_summaries_response():
    test_data = {
        "country": "mw_test",
        "station_id": "fake_station_id",
        "summaries": [
            "annual_rain",
            "start_rains",
            "end_rains",
            "end_season",
            "seasonal_rain",
            "seasonal_length"
        ],
    }
    return client.post("/v1/annual_rainfall_summaries/", json=test_data)

def annual_temperature_summaries_response():
    test_data = {
        "country": "mw_test",
        "station_id": "fake_station_id",
        "summaries": [
            "mean_tmin",
            "mean_tmax",
            "min_tmin",
            "min_tmax",
            "max_tmin",
            "max_tmax"
        ],
    }
    return client.post("/v1/annual_temperature_summaries/", json=test_data)

def monthly_temperature_summaries_response():
    test_data = {
        "country": "mw_test",
        "station_id": "fake_station_id",
        "summaries": [
            "mean_tmin",
            "mean_tmax",
            "min_tmin",
            "min_tmax",
            "max_tmin",
            "max_tmax"
        ],
    }
    return client.post("/v1/monthly_temperature_summaries/", json=test_data)

def crop_success_probabilities_response():
    test_data = {
        "country": "mw_test",
        "station_id": "fake_station_id",
        "water_requirements": [100,200,300],
        "planting_length": [20],
        "planting_dates": [25,50,75],
        "start_before_season": True
    }
    return client.post("/v1/crop_success_probabilities/", json=test_data)

def season_start_probabilities_response():
    test_data = {
        "country": "mw_test",
        "station_id": "fake_station_id",
        "start_dates": [200,220,250,270,300,320]
    }
    return client.post("/v1/season_start_probabilities/", json=test_data)

def test_station_definitions_response_model_validation_error():
    app.dependency_overrides[get_run_epicsa_function] = get_mock_run_epicsa_function
    response = station_definitions_response()   
    assert response.status_code == 500
    assert "Response model validation error" in response.json()["detail"]
    app.dependency_overrides = {}  

def test_annual_rainfall_summaries_response_model_validation_error():
    app.dependency_overrides[get_run_epicsa_function] = get_mock_run_epicsa_function
    response = annual_rainfall_summaries_response()   
    assert response.status_code == 500
    assert "Response model validation error" in response.json()["detail"]
    app.dependency_overrides = {}  

def test_annual_temperature_summaries_response_model_validation_error():
    app.dependency_overrides[get_run_epicsa_function] = get_mock_run_epicsa_function
    response = annual_temperature_summaries_response()   
    assert response.status_code == 500
    assert "Response model validation error" in response.json()["detail"]
    app.dependency_overrides = {}  

def test_monthly_temperature_summaries_response_model_validation_error():
    app.dependency_overrides[get_run_epicsa_function] = get_mock_run_epicsa_function
    response = monthly_temperature_summaries_response()   
    assert response.status_code == 500
    assert "Response model validation error" in response.json()["detail"]
    app.dependency_overrides = {}  

def test_crop_success_probabilities_response_model_validation_error():
    app.dependency_overrides[get_run_epicsa_function] = get_mock_run_epicsa_function
    response = crop_success_probabilities_response()   
    assert response.status_code == 500
    assert "Response model validation error" in response.json()["detail"]
    app.dependency_overrides = {}

def test_season_start_probabilities_response_model_validation_error():
    app.dependency_overrides[get_run_epicsa_function] = get_mock_run_epicsa_function
    response = season_start_probabilities_response()   
    assert response.status_code == 500
    assert "Response model validation error" in response.json()["detail"]
    app.dependency_overrides = {}

def test_station_definitions_error():
    response = station_definitions_response()   
    assert response.status_code == 500

def test_annual_rainfall_summaries_error():
    response = annual_rainfall_summaries_response()   
    assert response.status_code == 500

def test_annual_temperature_summaries_error():
    response = annual_temperature_summaries_response()   
    assert response.status_code == 500

def test_monthly_temperature_summaries_error():
    response = monthly_temperature_summaries_response()   
    assert response.status_code == 500

def test_crop_success_probabilities_error():
    response = crop_success_probabilities_response()   
    assert response.status_code == 500

def test_season_start_probabilities_error():
    response = season_start_probabilities_response()   
    assert response.status_code == 500