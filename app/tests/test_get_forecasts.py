from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

def assert_result_structure(result):
    assert "forecasts" in result

def assert_country_structure(country):
    assert "id" in country[0]
    assert "date_modified" in country[0]
    assert "language" in country[0]
    assert "filename" in country[0]
    assert "district" in country[0]
    assert "type" in country[0]

def assert_country_not_set_up_zm(result):
    assert "detail" in result
    assert result["detail"] == "Seasonal Forecasts not set up 'zm'"

def test_get_forecasts_structure():
    response = client.get("/v1/forecasts")
    assert response.status_code == 200
    result = response.json()
    assert_result_structure(result)
    assert_country_structure(result["forecasts"]["mw"])

def test_get_forecasts_file():
    country = "mw"
    file_name = "-annual_forecast-en.pdf"
    response = client.get(f"/v1/forecasts/{country}/{file_name}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == f"attachment; filename={file_name}"

def test_get_forecasts_file_no_file():
    country = "mw"
    file_name = "nonexistent_file.pdf"
    response = client.get(f"/v1/forecasts/{country}/{file_name}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"File not found: {file_name}"

def test_get_forecasts_file_no_country():
    country = "invalid"
    file_name = "-annual_forecast-en.pdf"
    response = client.get(f"/v1/forecasts/{country}/{file_name}")
    assert response.status_code == 422


