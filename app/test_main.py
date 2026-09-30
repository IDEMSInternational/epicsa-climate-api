from requests import Response


from app.core.config import Settings
from .main import app, get_settings


def get_settings_override():
    return Settings(admin_email="testing_admin@example.com")


app.dependency_overrides[get_settings] = get_settings_override


def test_swagger_docs(client):
    response: Response = client.get("/")
    assert response.status_code == 200
    html: str = response.text
    assert html.find('<!DOCTYPE html>') > 0


def test_openapi_includes_database_schemas(client):
    response: Response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    schemas = data.get("components", {}).get("schemas", {})
    expected_models = [
        "CropRecord",
        "DefinitionRecord",
        "StationRecord",
        "SummaryRecord",
        "SummaryStationMetadataRecord",
    ]
    for model_name in expected_models:
        assert model_name in schemas, f"{model_name} should be in OpenAPI schemas"
        assert schemas[model_name]["type"] == "object"


def test_database_schemas_instantiation():
    from app.schemas.database import (
        CropRecord,
        DefinitionRecord,
        StationRecord,
        SummaryRecord,
        SummaryStationMetadataRecord,
    )

    crop = CropRecord(station_id="dodoma", year="2024", plant_day=15.0)
    assert crop.station_id == "dodoma"
    assert crop.plant_day == 15.0

    station = StationRecord(station_id="dodoma", latitude=-6.16, longitude=35.75)
    assert station.station_id == "dodoma"
    assert station.latitude == -6.16

