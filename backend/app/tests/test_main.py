from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_calendars():
    response = client.get("/calendars/")
    assert response.status_code == 200
