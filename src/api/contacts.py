from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.db.db import get_db
from src.db.models import User
from src.schemas import ContactModel, ContactResponse
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])
user_dependency = Annotated[User, Depends(get_current_user)]


def get_contact_service(db: AsyncSession = Depends(get_db)) -> ContactService:
    """
    Dependency to get the ContactService instance.

    Args:
        db (AsyncSession): The database session.

    Returns:
        ContactService: An instance of the contact service.
    """
    return ContactService(db)


def raise_not_found_error(detail: str = "Contact not found"):
    """
    Raise an HTTPException for not found errors.

    Args:
        detail (str): The error message to include in the exception.

    Raises:
        HTTPException: With 404 status code and the provided detail.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    user: user_dependency,
    days: int = Query(default=7, ge=1),
    contact_service: ContactService = Depends(get_contact_service),
):
    """
    Get a list of contacts with upcoming birthdays.

    Args:
        user: Request user.
        days (int): Number of days to look ahead for upcoming birthdays.
        contact_service (ContactService): The contact service instance.

    Returns:
        List[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    return await contact_service.list_upcoming_birthdays(user.id, days)


@router.get("/", response_model=List[ContactResponse])
async def get_all_contacts(
    user: user_dependency,
    first_name: str = "",
    last_name: str = "",
    email: str = "",
    skip: int = 0,
    limit: int = 100,
    contact_service: ContactService = Depends(get_contact_service),
):
    """
    Retrieve a list of all contacts with optional filters.

    Args:
        user: Request user.
        first_name (str): Filter contacts by first name (optional).
        last_name (str): Filter contacts by last name (optional).
        email (str): Filter contacts by email (optional).
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return.
        contact_service (ContactService): The contact service instance.

    Returns:
        List[ContactResponse]: A list of contacts matching the filters.
    """
    return await contact_service.list_contacts(user.id, first_name, last_name, email, skip, limit)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    user: user_dependency,
    contact_id: int,
    contact_service: ContactService = Depends(get_contact_service),
):
    """Retrieve a specific contact by ID."""
    contact = await contact_service.retrieve_contact(user.id, contact_id)
    if contact is None:
        raise_not_found_error()
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    user: user_dependency,
    body: ContactModel,
    contact_service: ContactService = Depends(get_contact_service),
):
    """
    Create a new contact.

    Args:
        user: Request user.
        body (ContactModel): The data for the new contact.
        contact_service (ContactService): The contact service instance.

    Returns:
        ContactResponse: The created contact.
    """
    return await contact_service.create_contact(user.id, body)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    user: user_dependency,
    contact_id: int,
    contact_service: ContactService = Depends(get_contact_service),
):
    """
    Update an existing contact.

    Args:
        body (ContactModel): The updated data for the contact.
        user: Request user.
        contact_id (int): The ID of the contact to update.
        contact_service (ContactService): The contact service instance.

    Returns:
        ContactResponse: The updated contact.

    Raises:
        HTTPException: If the contact with the specified ID is not found.
    """
    contact = await contact_service.modify_contact(user.id, contact_id, body)
    if contact is None:
        raise_not_found_error()
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    user: user_dependency,
    contact_id: int,
    contact_service: ContactService = Depends(get_contact_service),
):
    """Delete a specific contact by ID."""
    contact = await contact_service.delete_contact(user.id, contact_id)
    if contact is None:
        raise_not_found_error()
    return contact
