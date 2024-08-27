import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

username = "testuser"
password = "testpassword"


def test_register_user():
    response = client.post("/register", json={"username": username, "password": password})

    if 'detail' in response.json():
        assert response.status_code == 400
        assert response.json()["detail"] == "Такой пользователь уже есть!"
    else:
        assert response.status_code == 200
        assert response.json()["message"] == "Пользователь зарегестрирован!"


def test_login():
    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_create_note():
    response = client.post("/token", data={"username": username, "password": password})
    access_token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    note_data = {"title": "Тест", "content": "Эта заметка создана тестом"}

    response = client.post("/notes", json=note_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Заметка добавлена"


def test_create_note_with_errors():
    response = client.post("/token", data={"username": username, "password": password})
    access_token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    note_data = {"title": "Тест замитка", "content": "Ошабки должни испровится"}

    response = client.post("/notes", json=note_data, headers=headers)
    assert response.status_code == 200
    assert (response.json()["message"] == "Заметка добавлена" and
            response.json()["title"] == "Тест заметка" and
            response.json()["content"] == "Ошибки должны исправиться")


def test_get_notes():
    response = client.post("/token", data={"username": username, "password": password})
    access_token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/notes", headers=headers)

    assert response.status_code == 200
    assert "message" in response.json()[0]
