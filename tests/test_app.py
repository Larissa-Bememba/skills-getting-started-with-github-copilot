import os
import sys

# Ensure `src` is on the path so we can import `app` directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data


def test_signup_and_unregister_flow():
    activity = "Basketball Team"
    email = "testuser@example.com"

    # Ensure clean state
    client.post(f"/activities/{activity}/unregister?email={email}")

    # Signup
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert "Signed up" in res.json().get("message", "")

    # Verify participant present
    res = client.get("/activities")
    assert email in res.json()[activity]["participants"]

    # Unregister
    res = client.post(f"/activities/{activity}/unregister?email={email}")
    assert res.status_code == 200
    assert "Unregistered" in res.json().get("message", "")

    # Verify removed
    res = client.get("/activities")
    assert email not in res.json()[activity]["participants"]


def test_duplicate_signup_returns_400():
    activity = "Basketball Team"
    email = "dup@example.com"

    # Cleanup
    client.post(f"/activities/{activity}/unregister?email={email}")

    # First signup succeeds
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200

    # Duplicate signup should fail
    res2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert res2.status_code == 400

    # Cleanup
    client.post(f"/activities/{activity}/unregister?email={email}")
