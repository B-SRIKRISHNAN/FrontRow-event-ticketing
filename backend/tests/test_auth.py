import pytest
import uuid

@pytest.mark.asyncio
async def test_auth_register_and_login(async_client):
    random_email = f"user_{uuid.uuid4().hex[:8]}@frontrow.com"
    password = "TestPassword123!"

    # 1. Register
    reg_resp = await async_client.post(
        "/api/v1/auth/register",
        json={"email": random_email, "password": password},
    )
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["token_type"] == "bearer"

    # 2. Duplicate Register Failure
    dup_resp = await async_client.post(
        "/api/v1/auth/register",
        json={"email": random_email, "password": password},
    )
    assert dup_resp.status_code == 400

    # 3. Login
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": random_email, "password": password},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data

    # 4. Login Invalid Credentials Failure
    bad_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": random_email, "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401
