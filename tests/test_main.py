from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_flight_data():
    # We mock the scraper to avoid hitting external sites in API tests
    # But for now, let's just check the endpoint exists
    response = client.get("/api/flight-data")
    assert response.status_code == 200
    data = response.json()
    assert "flight_id" in data
