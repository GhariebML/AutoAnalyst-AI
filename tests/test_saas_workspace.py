import pytest
from httpx import AsyncClient, ASGITransport
from adpilot.api.main import app
from adpilot.core.database import async_session_factory
from adpilot.models.user import User
from adpilot.models.organization import Organization
from sqlalchemy import select


@pytest.mark.anyio
async def test_user_registration_and_login():
    """Verify registration creates users and organizations, and login returns bearer tokens."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register organization and user
        register_payload = {
            "email": "test_saas_user@example.com",
            "password": "securepassword123",
            "role": "marketer",
            "organizationName": "Test Acme SaaS Inc",
        }
        res = await ac.post("/api/auth/register", json=register_payload)
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "test_saas_user@example.com"
        assert data["role"] == "marketer"
        assert "userId" in data
        assert "organizationId" in data
        
        user_id = data["userId"]
        org_id = data["organizationId"]

        # Verify database entities
        async with async_session_factory() as session:
            db_user = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
            assert db_user is not None
            assert db_user.email == "test_saas_user@example.com"
            assert db_user.role == "marketer"

            db_org = (await session.execute(select(Organization).where(Organization.id == org_id))).scalar_one_or_none()
            assert db_org is not None
            assert db_org.name == "Test Acme SaaS Inc"

        # 2. Login
        login_payload = {
            "email": "test_saas_user@example.com",
            "password": "securepassword123",
        }
        res_login = await ac.post("/api/auth/login", json=login_payload)
        assert res_login.status_code == 200
        login_data = res_login.json()
        assert login_data["token"] == user_id
        assert login_data["role"] == "marketer"
        assert login_data["organizationId"] == org_id

        # 3. Duplicate Registration rejection
        res_dup = await ac.post("/api/auth/register", json=register_payload)
        assert res_dup.status_code == 400
        assert "already registered" in res_dup.json()["detail"]
