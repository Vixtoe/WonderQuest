from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch("main.save_attempt")
def test_create_progress(mock_save):
    mock_save.return_value = {
        "id": "test-uuid-123",
        "user_id": "victor",
        "task_goal": "Analyze pattern",
        "user_attempt": "1, 2, 4, 8",
        "hint_level": 0,
        "is_solved": True,
        "created_at": "2026-03-30T00:00:00+00:00"
    }

    response = client.post(
        "/api/progress",
        json={
            "user_id": "victor",
            "task_goal": "Analyze pattern",
            "user_attempt": "1, 2, 4, 8",
            "hint_level": 0,
            "is_solved": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "test-uuid-123"
    assert data["user_id"] == "victor"

@patch("main.get_attempts")
def test_read_user_progress_success(mock_get):
    mock_get.return_value = [
        {
            "id": "test-uuid-123",
            "user_id": "victor",
            "task_goal": "Analyze pattern",
            "user_attempt": "1, 2, 4, 8",
            "hint_level": 0,
            "is_solved": True,
            "created_at": "2026-03-30T00:00:00+00:00"
        }
    ]

    response = client.get("/api/progress/victor")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == "victor"

@patch("main.get_attempts")
def test_read_user_progress_not_found(mock_get):
    mock_get.return_value = []

    response = client.get("/api/progress/unknown_user")
    assert response.status_code == 404
    assert "No attempts found" in response.json()["detail"]

@patch("main.get_attempts")
def test_read_user_progress_server_error(mock_get):
    mock_get.side_effect = Exception("Connection timeout")

    response = client.get("/api/progress/victor")
    assert response.status_code == 500
    assert "Database query failed" in response.json()["detail"]