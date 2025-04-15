import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, Contact
from src.repositories.contacts import ContactRepository
from src.schemas import UserCreate, ContactModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session):
    data = ContactModel(first_name="Anna", last_name="Smith", email="anna@example.com", phone_number="44444444", birthday_date="1995-03-10")

    result = await contact_repository.create_contact(data)

    assert result.first_name == "Anna"
    mock_session.add.assert_called()
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mocker, mock_session):

    mock_contact = Contact(id=1, first_name="Test", last_name="User", email="test@example.com")

    mocker.patch.object(ContactRepository, "get_contact_by_id", new=mocker.AsyncMock(return_value=mock_contact))

    result = await contact_repository.get_contact_by_id(1)

    assert result.id == 1
    assert result.first_name == "Test"


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mocker, mock_session):
    mock_contact = Contact(id=1, first_name="Old", last_name="Name", email="old@example.com")

    mocker.patch.object(ContactRepository, 'get_contact_by_id', return_value=mock_contact)

    updated_data = ContactModel(first_name="New", last_name="Name", email="new@example.com", phone_number="34567890", birthday_date="1990-01-01")
    result = await contact_repository.update_contact(1, updated_data)

    assert result.first_name == "New"
    assert result.email == "new@example.com"
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mocker, mock_session):
    mock_contact = Contact(id=1, email="del@example.com")

    mocker.patch.object(ContactRepository, 'get_contact_by_id', return_value=mock_contact)

    result = await contact_repository.remove_contact(1)

    assert result.email == "del@example.com"
    mock_session.delete.assert_called_with(mock_contact)
    mock_session.commit.assert_called()


@pytest.mark.asyncio
async def test_does_contact_exist_non_existing_contact(contact_repository, mock_session):
    mock_execute = AsyncMock()
    mock_execute.scalars.return_value.first.return_value = None

    mock_session.execute = mock_execute

    result = await contact_repository.does_contact_exist("nonexistent@example.com", "9876543210")

    assert result is False
