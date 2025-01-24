import pytest
from fastapi.testclient import TestClient
from urllib.parse import urlencode
from collections import OrderedDict
from app.main import app

client = TestClient(app)


@pytest.mark.skip()
def test_get_documents():
    country = 'mw'
    query_string = urlencode(OrderedDict(match_glob="**evening**"))
    response = client.get(f"/v1/documents/{country}?{query_string}")
    assert response.status_code == 200
