from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app instance is named 'app'

client = TestClient(app)

def assert_data_structure_country_info(data):
    assert "station_id" in data
    assert "station_name" in data
    assert "latitude" in data
    assert "longitude" in data
    assert "elevation" in data
    assert "district" in data
    assert "country_code" in data

def assert_data_structure_definitions(data):
    assert  "start_rains.threshold" in data
    assert "start_rains.start_day" in data
    assert "start_rains.end_day" in data
    assert "start_rains.total_rainfall" in data
    assert "start_rains.amount_rain" in data
    assert "start_rains.over_days" in data
    assert "start_rains.proportion" in data
    assert "start_rains.number_rain_days" in data
    assert "start_rains.dry_spell" in data
    assert "start_rains.spell_max_dry_days" in data
    assert "start_rains.spell_interval" in data
    assert "start_rains.dry_period" in data
    assert "start_rains._last_updated" in data
    assert "end_rains.start_day" in data
    assert "end_rains.end_day" in data
    assert "end_rains.interval_length" in data
    assert "end_rains.min_rainfall" in data
    assert "end_season.start_day" in data
    assert "end_season.end_day" in data
    assert "end_season.capacity" in data
    assert "end_season.water_balance_max" in data
    assert "end_season.evaporation" in data
    assert "end_season.evaporation_value" in data
    assert "seasonal_total_rainfall.na_prop" in data
    assert "mean_tmax.to" in data
    assert "mean_tmax.na_rm" in data
    assert "mean_tmin.to" in data
    assert "mean_tmin.na_rm" in data
    assert  "annual_rain.annual_rain" in data
    assert "annual_rain.n_rain" in data
    assert "annual_rain.na_rm" in data
    assert "season_start_probabilities.specified_day.val1" in data
    assert "season_start_probabilities.specified_day.val2" in data
    assert "season_start_probabilities.specified_day.val3" in data
    assert "seasonal_rain.seasonal_rain" in data
    assert "seasonal_rain.n_rain" in data
    assert "seasonal_rain.na_rm" in data
    assert "seasonal_rain.rain_day" in data
    assert "crops_success.water_requirements.val1" in data
    assert "crops_success.water_requirements.val2" in data
    assert "crops_success.water_requirements.val3" in data
    assert "crops_success.planting_dates.val1" in data
    assert "crops_success.planting_dates.val2" in data
    assert "crops_success.planting_dates.val3" in data
    assert "crops_success.planting_length.val1" in data
    assert "crops_success.planting_length.val2" in data
    assert "crops_success.start_check" in data


def test_get_station_structure_all():
    response = client.get("/v1/station/")

    assert response.status_code == 200

    result = response.json()

    assert_data_structure_country_info(result["data"][0])
    assert_data_structure_definitions(result["data"][0])

def test_get_station_structure_zm():
    country = "zm"
    response = client.get(f"/v1/station/{country}")

    assert response.status_code == 200

    result = response.json()

    assert_data_structure_country_info(result["data"][0])
    assert_data_structure_definitions(result["data"][0])

def test_get_station_structure_zm_16():
    country = "zm"
    station = "16"
    response = client.get(f"/v1/station/{country}/{station}")

    assert response.status_code == 200

    result = response.json()

    assert_data_structure_country_info(result["data"][0])
    assert_data_structure_definitions(result["data"][0])