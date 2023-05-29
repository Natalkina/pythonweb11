from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session
from pydantic import EmailStr


from src.schemas import ContactModel, ContactUpdate, ContactResponse, ContactStatusUpdate, ContactResponseChoice
from src.repository import contacts as repository_contacts
from src.database.db import get_db
from src.database.models import Contact, User
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):

    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database session to the repository
    :param current_user: User: Get the user who is logged in
    :return: A contactmodel object

    """
    contact = await repository_contacts.create_contact(body, db, current_user)
    return contact


@router.get('/', response_model=List[ContactResponse],  description='No more than 10 requests per minute', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):

    """
    The get_contacts function returns a list of contacts.

    :param skip: int: Skip a number of contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user_id of the current user
    :return: A list of contacts

    """
    contacts = await repository_contacts.get_contacts(limit, skip, db, current_user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):

    """
    The get_contact function returns a contact by its id.

    :param contact_id: int: Get the contact id from the url
    :param db: Session: Access the database
    :param current_user: User: Get the current user from the database
    :return: A contact object

    """
    contact = await repository_contacts.get_contact_by_id(contact_id, db, current_user)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):

    """
    The update_contact function updates a contact in the database.

    :param body: ContactUpdate: Pass the contact information to be updated
    :param contact_id: int: Identify the contact to be deleted
    :param db: Session: Pass the database session to the repository
    :param current_user: User: Get the user_id of the current user
    :return: The updated contact

    """
    contact = await repository_contacts.update_contact(body, contact_id, db, current_user)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/by/", response_model=ContactResponseChoice)
async def get_contacts_by(name: str | None = None, surname: str | None = None, email: EmailStr | None = None, db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):

    """
    The get_contacts_by function returns a list of contacts that match the given name, surname and/or email.
    If no contact is found, an empty list is returned.

    :param name: str | None: Search for a contact by name
    :param surname: str | None: Filter the contacts by surname
    :param email: EmailStr | None: Validate the email address
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the user who is currently logged in
    :return: A contact object

    """
    contact = await repository_contacts.get_contacts_by(name, surname, email, db, current_user)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    print(f"name: {name}, surname: {surname}, email: {email}")
    return contact


@router.get("/birthdays/", response_model=List[ContactResponse])
async def get_contacts_birthdays(db: Session = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):

    """
    The get_contacts_birthdays function returns a list of contacts with birthdays in the current month.
        The function takes two parameters: db and current_user.
        The db parameter is used to access the database, while the current_user parameter is used to get information about who's logged in.

    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A list of contacts who have birthdays in the next 7 days

    """
    contacts = await repository_contacts.get_contacts_birthdays(db, current_user)

    return contacts


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):

    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Identify the contact to be deleted
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: The contact that was removed

    """
    contact = await repository_contacts.remove_contact(contact_id, db, current_user)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact

