from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.contacts import ContactRepository
from src.schemas import ContactModel


class ContactService:
    """
    Service class for managing contact-related operations.

    This class provides a higher-level interface for working with contacts,
    leveraging the `ContactRepository` for database interactions.

    Attributes:
        _repository (ContactRepository): Repository for performing database operations on contacts.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the ContactService with a database session.

        Args:
            db (AsyncSession): The asynchronous database session.
        """
        self._repository = ContactRepository(db)

    async def create_contact(self, user_id: int, data: ContactModel):
        """
        Create a new contact.

        Args:
            user_id: Request user.
            data (ContactModel): The contact data to create.

        Returns:
            Contact: The created contact.

        Raises:
            HTTPException: If a contact with the same email or phone number already exists.
        """
        existing_contact = await self._repository.does_contact_exist(user_id, data.email, data.phone_number)
        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact with email '{data.email}' or phone '{data.phone_number}' already exists."
            )
        return await self._repository.create_contact(data)

    async def list_contacts(
        self, user_id: int, first_name: str = "", last_name: str = "", email: str = "", skip: int = 0, limit: int = 100
    ):
        """
        Retrieve a list of contacts with optional filters.

        Args:
            user_id (str): Filter by user ID.
            first_name (str): Filter by first name (substring match). Default is "".
            last_name (str): Filter by last name (substring match). Default is "".
            email (str): Filter by email (substring match). Default is "".
            skip (int): Number of records to skip for pagination. Default is 0.
            limit (int): Maximum number of records to return. Default is 100.

        Returns:
            List[Contact]: A list of contacts matching the filters.
        """
        filters = {"user_id": user_id, "first_name": first_name, "last_name": last_name, "email": email}
        return await self._repository.get_contacts(**filters, skip=skip, limit=limit)

    async def retrieve_contact(self, user_id: int,  contact_id: int):
        """
        Retrieve a contact by its ID.

        Args:
            user_id (int): The ID of the contact to retrieve.
            contact_id (int): The ID of the contact to retrieve.

        Returns:
            Contact: The retrieved contact.

        Raises:
            HTTPException: If no contact exists with the given ID.
        """
        contact = await self._repository.get_contact_by_id(user_id, contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact with ID {contact_id} not found."
            )
        return contact

    async def modify_contact(self, user_id: int, contact_id: int, data: ContactModel):
        """
        Update an existing contact.

        Args:
            user_id (int): The ID of the user.
            contact_id (int): The ID of the contact to update.
            data (ContactModel): The new contact data.

        Returns:
            Contact: The updated contact.

        Raises:
            HTTPException: If the contact does not exist or cannot be updated.
        """
        updated_contact = await self._repository.update_contact(user_id, contact_id, data)
        if not updated_contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to update contact with ID {contact_id}. It may not exist."
            )
        return updated_contact

    async def delete_contact(self, user_id: int, contact_id: int):
        """
        Delete a contact by its ID.

        Args:
            user_id (int): The ID of the user.
            contact_id (int): The ID of the contact to delete.

        Returns:
            Contact: The deleted contact.

        Raises:
            HTTPException: If the contact does not exist or cannot be deleted.
        """
        deleted_contact = await self._repository.remove_contact(user_id, contact_id)
        if not deleted_contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to delete contact with ID {contact_id}. It may not exist."
            )
        return deleted_contact

    async def list_upcoming_birthdays(self, user_id: int, days: int):
        """
        Retrieve a list of contacts with upcoming birthdays within a specified number of days.

        Args:
            user_id (int): The ID of user.
            days (int): The number of days to look ahead for upcoming birthdays.

        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        return await self._repository.get_upcoming_birthdays(user_id, days)
