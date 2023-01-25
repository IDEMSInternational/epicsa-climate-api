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
