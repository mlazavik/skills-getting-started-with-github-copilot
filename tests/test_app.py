from copy import deepcopy

from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = deepcopy(app_module.activities)


def reset_activities() -> None:
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))


def setup_function() -> None:
    reset_activities()


def teardown_function() -> None:
    reset_activities()


def test_root_redirects_to_static_index() -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seeded_data() -> None:
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_for_activity_adds_participant() -> None:
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_for_activity_rejects_duplicate_email() -> None:
    email = "michael@mergington.edu"

    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_activity_rejects_unknown_activity() -> None:
    response = client.post("/activities/Unknown%20Activity/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_existing_participant() -> None:
    email = "michael@mergington.edu"

    response = client.post(f"/activities/Chess%20Club/unregister?email={email}")

    assert response.status_code == 200
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity() -> None:
    response = client.post("/activities/Unknown%20Activity/unregister?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_not_signed_up_student() -> None:
    response = client.post("/activities/Chess%20Club/unregister?email=absent@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
