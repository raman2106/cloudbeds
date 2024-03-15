from fastapi.testclient import TestClient
from src.utils import api

client = TestClient(api)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"app": "CloudBeds V1.0"}