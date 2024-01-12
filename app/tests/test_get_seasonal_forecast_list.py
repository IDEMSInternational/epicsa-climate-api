from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

def assert_result_structure(result):
    assert "districts" in result

def assert_country_not_set_up_zm(result):
    assert "detail" in result
    assert result["detail"] == "Seasonal Forecasts not set up 'zm'"

def test_get_seasonal_forecast_list_structure_mw_balaka():
    # Define test input data
    test_data = {
        "country": "mw",
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/seasonal_forecast_list/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)


def test_get_seasonal_forecast_list_data_zm_error():
    # Define test input data
    test_data = {
        "country": "zm",
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/seasonal_forecast_list/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 404

    result = response.json()

    assert_country_not_set_up_zm(result)