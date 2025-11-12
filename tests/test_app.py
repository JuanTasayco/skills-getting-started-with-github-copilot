from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of initial participants so tests can mutate safely
    original = {k: v["participants"].copy() for k, v in activities.items()}
    yield
    # restore
    for k, v in activities.items():
        v["participants"] = original[k].copy()


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_student@mergington.edu"

    # Ensure not already signed up
    assert email not in activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")
    assert email in activities[activity]["participants"]

    # Signing up again should fail
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400

    # Unregister
    resp3 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp3.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_student():
    activity = "Chess Club"
    email = "nobody@mergington.edu"
    # Ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 400
