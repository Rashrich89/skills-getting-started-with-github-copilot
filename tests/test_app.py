import pytest
from fastapi.testclient import TestClient
from src.app import app


def test_root_redirect(client: TestClient):
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/")
    assert response.status_code == 200
    # FastAPI TestClient follows redirects by default
    assert "/static/index.html" in response.url


def test_get_activities(client: TestClient):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check that each activity has the required fields
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_for_activity_success(client: TestClient):
    """Test successful signup for an activity"""
    # Use an activity that exists
    activity_name = "Chess Club"
    email = "test@example.com"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_for_activity_not_found(client: TestClient):
    """Test signup for non-existent activity"""
    response = client.post(
        "/activities/NonExistentActivity/signup",
        params={"email": "test@example.com"}
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_for_activity_already_signed_up(client: TestClient):
    """Test signup when student is already signed up"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is already in Chess Club

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_unregister_from_activity_success(client: TestClient):
    """Test successful unregistration from an activity"""
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # This email is in Programming Class

    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_unregister_from_activity_not_found(client: TestClient):
    """Test unregister from non-existent activity"""
    response = client.delete(
        "/activities/NonExistentActivity/unregister",
        params={"email": "test@example.com"}
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_from_activity_not_signed_up(client: TestClient):
    """Test unregister when student is not signed up"""
    activity_name = "Chess Club"
    email = "notsignedup@example.com"

    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_signup_and_unregister_integration(client: TestClient):
    """Test that signup and unregister work together correctly"""
    activity_name = "Gym Class"
    email = "integration@test.com"

    # First, sign up
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200

    # Check that the participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity_name]["participants"]

    # Then unregister
    unregister_response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert unregister_response.status_code == 200

    # Check that the participant was removed
    activities_response2 = client.get("/activities")
    activities_data2 = activities_response2.json()
    assert email not in activities_data2[activity_name]["participants"]