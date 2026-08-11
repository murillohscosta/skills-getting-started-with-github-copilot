import uuid
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_activity_data():
    # Arrange
    expected_activities = {"Chess Club", "Programming Class"}

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(activities, dict)
    assert expected_activities.issubset(set(activities.keys()))


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = f"test_signup_{uuid.uuid4().hex}@mergington.edu"
    signup_path = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.post(signup_path)
    updated = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in updated[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate():
    # Arrange
    activity_name = "Programming Class"
    email = f"test_duplicate_{uuid.uuid4().hex}@mergington.edu"
    signup_path = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    first_response = client.post(signup_path)
    duplicate_response = client.post(signup_path)

    # Assert
    assert first_response.status_code == 200
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Gym Class"
    email = f"test_remove_{uuid.uuid4().hex}@mergington.edu"
    signup_path = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    delete_path = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    # Act
    signup_response = client.post(signup_path)
    delete_response = client.delete(delete_path)
    updated = client.get("/activities").json()

    # Assert
    assert signup_response.status_code == 200
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in updated[activity_name]["participants"]


def test_remove_unknown_participant_returns_404():
    # Arrange
    activity_name = "Art Studio"
    email = f"test_unknown_{uuid.uuid4().hex}@mergington.edu"
    delete_path = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    # Act
    delete_response = client.delete(delete_path)

    # Assert
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Participant not found"


def test_root_redirects_to_static_index():
    # Arrange / Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"
