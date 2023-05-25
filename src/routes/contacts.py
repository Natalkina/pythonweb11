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
    contact = await repository_contacts.create_contact(body, db, current_user)
    return contact


@router.get('/', response_model=List[ContactResponse],  description='No more than 10 requests per minute', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(limit, skip, db, current_user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact_by_id(contact_id, db, current_user)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(body, contact_id, db, current_user)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.get("/by/", response_model=ContactResponseChoice)
async def get_contacts_by(name: str | None = None, surname: str | None = None, email: EmailStr | None = None, db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contacts_by(name, surname, email, db, current_user)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    print(f"name: {name}, surname: {surname}, email: {email}")
    return contact


@router.get("/birthdays/", response_model=List[ContactResponse])
async def get_contacts_birthdays(db: Session = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts_birthdays(db, current_user)

    return contacts


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, db, current_user)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact

