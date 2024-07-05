import pytest
from fastapi.testclient import TestClient
from fj_blitz.auth_fastAPI import app

client = TestClient(app)

@pytest.fixture(scope="module")
def register_user():
    response = client.post(
        "/register/",
        json={"username": "test_user", "password": "test_password", "password_confirm": "test_password", "email": "test@example.com"}
    )
    assert response.status_code == 200
    return response.json()

@pytest.mark.parametrize("username, password, expected_status_code", [
    ("test_user", "wrong_password", 401),
    ("non_existing_user", "some_password", 401)
])
def test_authenticate_user(username, password, expected_status_code, register_user):
    response = client.post(
        "/login/",
        data={"username": username, "password": password}
    )
    assert response.status_code == expected_status_code

@pytest.mark.parametrize("topic_input", ["topic1", "topic2"])
def test_generate_mcqs(topic_input, register_user):
    response = client.post(
        "/generate_mcqs/",
        json={"topic_input": topic_input}
    )
    assert response.status_code == 200
    assert "mcqs" in response.json()

@pytest.mark.parametrize("result, collected_answers", [
    ("result1", "collected_answers1"),
    ("result2", "collected_answers2")
])
def test_generate_result(result, collected_answers, register_user):
    response = client.post(
        "/generate_result/",
        json={"result": result, "collected_answers": collected_answers}
    )
    assert response.status_code == 200
    assert "result1" in response.json()
    assert "result2" in response.json()
    assert "result3" in response.json()
