import asyncio

from unittest.mock import MagicMock

from src.database.models import User
from src.services.auth import auth_service


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)


    response = client.post(
        "/api/auth/signup",
        json=user,
    )

    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_user_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_user_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": "email@email.com", "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"

def test_refresh_token_success( user, session, client):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()

    response = client.get(
        f"/api/auth/refresh_token",
        headers={"Authorization": f"Bearer {current_user.refresh_token}"}
    )

    assert response.status_code == 200, response.text
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_invalid_token(user, client):
    invalid_refresh_token = asyncio.run(auth_service.create_refresh_token(
        data={"sub": user['email']}, expires_delta=100)
    )

    response = client.get(
        f"/api/auth/refresh_token",
        headers={"Authorization": f"Bearer {invalid_refresh_token}"}
    )

    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Invalid refresh token"

def test_confirmed_email(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()

    token = asyncio.run(auth_service.create_email_token(data={"sub": user["email"]}))
    response = client.get(f"/api/auth/confirmed_email/{token}")

    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Email confirmed"}


    current_user.confirmed = True
    session.commit()
    response = client.get(f"/api/auth/confirmed_email/{token}")
    assert response.status_code == 200
    assert response.json() == {"message": "Your email is already confirmed"}


def test_confirmed_email_user_invalid(client, session, user):

    token = asyncio.run(auth_service.create_email_token(data={"sub": "invalid@mial.com"}))
    response = client.get(f"/api/auth/confirmed_email/{token}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Verification error"}



def test_request_email_already_confirmed(user, client, session):
    response = client.post(
        f"/api/auth/request_email",
        json={"email": user["email"]}
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'message': 'Your email is already confirmed'}

def test_request_email_user_not_found(user, client, session):

    response = client.post(
        f"/api/auth/request_email",
        json={"email": "invalid@test.com"}
    )

    assert response.status_code == 400, response.text
    assert response.json() == {"detail": "Verification error"}


def test_request_email_successfully_confirmed(user, client, session, monkeypatch):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()

    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    response = client.post(
        f"/api/auth/request_email",
        json={"email": user["email"]}
    )
    print(response.text)
    print(response.status_code)
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Check your email for confirmation."}

