import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Arrange: reload module so memory store resets between tests
    mod = importlib.reload(__import__("src.app", fromlist=["app", "activities"]))
    return TestClient(mod.app)


def test_get_activities(client):
    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_duplicate(client):
    # Arrange
    email = "test@school.edu"
    activity = "Chess%20Club"

    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Act - duplicate signup
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert resp2.status_code == 400
    assert "already signed up" in resp2.json()["detail"]


def test_delete_participant(client):
    # Arrange - first add a participant
    email = "deleteme@school.edu"
    activity = "Chess%20Club"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    del_res = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert del_res.status_code == 200
    assert "Removed" in del_res.json()["message"]
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_errors_for_missing_resources(client):
    # Act & Assert
    r1 = client.post("/activities/NotAThing/signup?email=a@b.com")
    assert r1.status_code == 404

    r2 = client.delete("/activities/NotAThing/signup?email=a@b.com")
    assert r2.status_code == 404

    r3 = client.delete("/activities/Chess%20Club/signup?email=nope@x.com")
    assert r3.status_code == 404
