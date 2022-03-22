import pytest

from fastapi_auth.repo import Repo
from fastapi_auth.services.admin import AdminService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_service(mock_repo: Repo):
    yield AdminService(mock_repo)


async def test_ban(mock_service: AdminService):
    await mock_service.ban(1)


async def test_unban(mock_service: AdminService):
    await mock_service.unban(1)


async def test_kick(mock_service: AdminService):
    await mock_service.kick(1)


async def test_unkick(mock_service: AdminService):
    await mock_service.unkick(1)


async def test_set_roles(mock_service: AdminService):
    await mock_service.set_roles(1, ["role"])


async def test_get_mass_logout_status_not_active(mock_service: AdminService):
    status = await mock_service.get_mass_logout_status()
    assert status.active is False
    assert status.date is None


async def test_get_mass_logout_status_active(mock_service: AdminService):
    await mock_service.activate_mass_logout()
    status = await mock_service.get_mass_logout_status()
    assert status.active is True
    assert status.date is not None


async def test_activate_mass_logout(mock_service: AdminService):
    await mock_service.activate_mass_logout()


async def test_deactivate_mass_logout(mock_service: AdminService):
    await mock_service.deactivate_mass_logout()
