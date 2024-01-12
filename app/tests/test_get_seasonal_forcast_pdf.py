from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

def assert_result_structure(result):
    assert "pdf_url" in result


def test_get_seasonal_forecast_pdf_structure_mw_balaka():
    # Define test input data
    test_data = {
        "country": "mw",
        "district": "balaka",
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/seasonal_forecast_pdf/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 200

    result = response.json()

    assert_result_structure(result)


def test_get_seasonal_forecast_pdf_data_zm_error():
    # Define test input data
    test_data = {
        "country": "zm",
        "district": "anything",
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/seasonal_forecast_pdf/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 404

    result = response.json()

    assert result["detail"] == "Seasonal Forecasts not set up 'zm'"

def test_get_seasonal_forecast_pdf_data_mw_wrong_district_error():
    # Define test input data
    test_data = {
        "country": "mw",
        "district": "wrong_district",
    }

    # Make a request to the endpoint using the TestClient
    response = client.post("/v1/seasonal_forecast_pdf/", json=test_data)

    # Check that the response has a 200 status code
    assert response.status_code == 404

    result = response.json()

    assert result["detail"] == "PDF link not found for 'wrong_district'"