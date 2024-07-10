import pytest
from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app instance is named 'app'

client = TestClient(app)

def assert_annual_rainfall_summaries(country, station_id):
    test_data = {
        "country": country,
        "station_id": station_id,
        "summaries": [
            "annual_rain",
            "start_rains",
            "end_rains",
            "end_season",
            "seasonal_rain",
            "seasonal_length"
        ],
    }
    response = client.post("/v1/annual_rainfall_summaries/", json=test_data)
    assert response.status_code == 200

def assert_annual_temperature_summaries(country, station_id):
    test_data = {
        "country": country,
        "station_id": station_id,
        "summaries": [
            "mean_tmin",
            "mean_tmax",
            "min_tmin",
            "min_tmax",
            "max_tmin",
            "max_tmax"
        ],
    }
    response = client.post("/v1/annual_temperature_summaries/", json=test_data)
    assert response.status_code == 200

def assert_monthly_temperature_summaries(country, station_id):
    test_data = {
        "country": country,
        "station_id": station_id,
        "summaries": [
            "mean_tmin",
            "mean_tmax",
            "min_tmin",
            "min_tmax",
            "max_tmin",
            "max_tmax"
        ],
    }
    response = client.post("/v1/monthly_temperature_summaries/", json=test_data)
    assert response.status_code == 200

def assert_crop_success_probabilities(country, station_id):
    test_data = {
        "country": country,
        "station_id": station_id,
        "water_requirements": [100,200,300],
        "planting_length": [20],
        "planting_dates": [25,50,75],
        "start_before_season": True
    }
    response = client.post("/v1/crop_success_probabilities/", json=test_data)
    assert response.status_code == 200

def assert_season_start_probabilities(country, station_id):
    test_data = {
        "country": country,
        "station_id": station_id,
        "start_dates": [200,220,250,270,300,320]
    }
    response = client.post("/v1/season_start_probabilities/", json=test_data)
    assert response.status_code == 200

def assert_extremes_summaries(country, station_id):
    return #Not tested at moment as not completed
    test_data = {
        "country": country,
        "station_id": station_id,
        "summaries": [
            "extremes_tmax",
            "extremes_tmin",
            "extremes_tmax"
        ],
    }
    response = client.post("/v1/extremes_summaries/", json=test_data)
    assert response.status_code == 200

def assert_station_definitions(country, station_id):
    response = client.get(f"/v1/station/{country}/{station_id}")
    assert response.status_code == 200

def test_zm_stations():
    country = "zm"
    assert_all_function_for_country(country)

def test_zm_test_stations():
    country = "zm_test"
    assert_all_function_for_country(country)

def test_zm_workshops_stations():
    country = "zm_workshops"
    assert_all_function_for_country(country)

def test_mw_stations():
    country = "mw"
    assert_all_function_for_country(country)

def test_mw_test_stations():
    country = "mw_test"
    assert_all_function_for_country(country)

def test_mw_workshops_stations():
    country = "mw_workshops"
    assert_all_function_for_country(country)


def assert_all_function_for_country(country):
    
    response = client.get(f"/v1/station/{country}")

    assert response.status_code == 200
    errors = []
    result = response.json()
    data = result["data"]
    for i in range(len(data)):
        station_id = data[i]["station_id"]
        print("stationid: " + station_id)

        try:
            assert_station_definitions(country,station_id)
        except AssertionError as e:
            errors.append(f"Failed: station definitions for country {country} station {station_id}")

        try:
            assert_annual_rainfall_summaries(country, station_id)
        except AssertionError as e:
            errors.append(f"Failed: annual rainfall summaries for country {country} station {station_id}")
        
        try:
            assert_annual_temperature_summaries(country, station_id)
        except AssertionError as e:
            errors.append(f"Failed: annual temperature summaries for country {country} station {station_id}")

   #     try:
   #         assert_crop_success_probabilities(country, station_id)
   #     except AssertionError as e:
   #         errors.append(f"Failed: crop success probabilities for country {country} station {station_id}")

        try:
            assert_monthly_temperature_summaries(country, station_id)
        except AssertionError as e:
            errors.append(f"Failed: monthly temperature summaries for country {country} station {station_id}")

        try:
            assert_season_start_probabilities(country, station_id)
        except AssertionError as e:
            errors.append(f"Failed: season start probabilities for country {country} station {station_id}")

        try:
            assert_extremes_summaries(country, station_id)
        except AssertionError as e:
            errors.append(f"Failed: extremes summaries for country {country} station {station_id}")

    if errors:
        for error in errors:
            print(error)
        raise AssertionError("Some assertions failed. Check the above errors.")

        