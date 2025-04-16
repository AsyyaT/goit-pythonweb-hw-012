import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status

from src.db.models import Contact
from src.services.contacts import ContactService
from src.schemas import ContactModel


@pytest.fixture
def contact_data():
    return ContactModel(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
        birthday_date="1990-01-01"
    )


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def contact_service(mock_repository):
    service = ContactService.__new__(ContactService)
    service._repository = mock_repository
    return service


@pytest.mark.asyncio
async def test_create_contact_success(contact_service, contact_data):
    contact_service._repository.does_contact_exist.return_value = False
    contact_service._repository.create_contact.return_value = Contact(**contact_data.dict())

    result = await contact_service.create_contact(user_id=1, data=contact_data)

    assert result.email == contact_data.email
    contact_service._repository.create_contact.assert_called_once()


@pytest.mark.asyncio
async def test_create_contact_duplicate(contact_service, contact_data):
    contact_service._repository.does_contact_exist.return_value = True

    with pytest.raises(HTTPException) as exc:
        await contact_service.create_contact(user_id=1, data=contact_data)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_retrieve_contact_not_found(contact_service):
    contact_service._repository.get_contact_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await contact_service.retrieve_contact(user_id=1, contact_id=1)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_contact_success(contact_service):
    contact = Contact(id=1)
    contact_service._repository.remove_contact.return_value = contact

    result = await contact_service.delete_contact(user_id=1, contact_id=1)

    assert result == contact


@pytest.mark.asyncio
async def test_list_contacts(contact_service):
    contact_service._repository.get_contacts.return_value = []

    result = await contact_service.list_contacts(user_id=1)

    assert isinstance(result, list)
