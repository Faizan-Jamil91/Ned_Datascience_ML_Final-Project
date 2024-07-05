import pytest
import requests
from fj_blitz.sys_StreamLit import main

@pytest.fixture(scope="module")
def base_url():
    return "http://127.0.0.1:8000"

def test_login(base_url):
    # Test successful login
    response = requests.post(f"{base_url}/login/", data={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200
    assert "token" in response.json()

    # Test login with incorrect password
    response = requests.post(f"{base_url}/login/", data={"username": "test_user", "password": "wrong_password"})
    assert response.status_code == 401

    # Test login with non-existing username
    response = requests.post(f"{base_url}/login/", data={"username": "non_existing_user", "password": "some_password"})
    assert response.status_code == 401

def test_register(base_url):
    # Test successful registration
    response = requests.post(f"{base_url}/register/", data={"username": "new_user", "password": "new_password", "password_confirm": "new_password", "email": "new_user@example.com"})
    assert response.status_code == 200

    # Test registration with existing username
    response = requests.post(f"{base_url}/register/", data={"username": "test_user", "password": "test_password", "password_confirm": "test_password", "email": "test_user@example.com"})
    assert response.status_code == 400

def test_generate_mcqs(base_url):
    # Test generate MCQs without authentication
    response = requests.post(f"{base_url}/generate_mcqs/", data={"topic_input": "topic"})
    assert response.status_code == 401

    # Test generate MCQs with authentication
    token = get_auth_token(base_url)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{base_url}/generate_mcqs/", data={"topic_input": "topic"}, headers=headers)
    assert response.status_code == 200
    assert "mcqs" in response.json()

def test_generate_result(base_url):
    # Test generate result without authentication
    response = requests.post(f"{base_url}/generate_result/", data={"result": "result", "collected_answers": "answers"})
    assert response.status_code == 401

    # Test generate result with authentication
    token = get_auth_token(base_url)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{base_url}/generate_result/", data={"result": "result", "collected_answers": "answers"}, headers=headers)
    assert response.status_code == 200
    assert "result" in response.json()

def get_auth_token(base_url):
    # Helper function to get authentication token
    response = requests.post(f"{base_url}/login/", data={"username": "test_user", "password": "test_password"})
    return response.json().get("token")
