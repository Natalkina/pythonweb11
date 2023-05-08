import datetime

from sqlalchemy import and_, or_, text
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactModel, ContactStatusUpdate


async def get_contacts(limit: int, offset: int,  db: Session):
    contact = db.query(Contact).limit(limit).offset(offset).all()
    return contact


async def get_contact_by_id(contact_id: int, db: Session):
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def create_contact(body: ContactModel, db: Session) -> Contact:
    contact = Contact(
        id=None,
        name=body.name,
        surname=body.surname,
        email=body.email,
        mobile=body.mobile,
        date_of_birth=body.date_of_birth,

    )


    try:
        db.add(contact)
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError("Failed to create user", str(e))
    db.refresh(contact)

    return contact


async def update_contact(body: ContactModel, contact_id: int, db: Session):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.mobile = body.mobile
        contact.date_of_birth = body.date_of_birth
        db.commit()
    return contact


async def get_contacts_by(name: str | None, surname: str | None, email: str | None, db: Session):
    contacts = db.query(Contact).filter(and_(or_(
        Contact.name == name, Contact.surname == surname, Contact.email == email)
    )
    )

    if name:
        contacts = contacts.filter(Contact.name.like(f"%{name}%"))
    if surname:
        contacts = contacts.filter(Contact.surname.like(f"%{surname}%"))
    if email:
        contacts = contacts.filter(Contact.email.like(f"%{email}%"))
    print(f"name: {name}, surname: {surname}, email: {email}")

    contact = contacts.first()
    return contact


async def get_contacts_birthdays(db: Session):
    query = text("SELECT * FROM contacts WHERE extract(month from date_of_birth) = extract(month from now() + interval '7 days') AND extract(day from date_of_birth) >= extract(day from now()) AND extract(day from date_of_birth) <= extract(day from now() + interval '7 days');")
    contacts = db.execute(query).fetchall()

    return contacts


async def remove_contact(contact_id: int, db: Session):
    contact = await get_contact_by_id(contact_id, db)

    if contact:
        db.delete(contact)
        db.commit()
    return contact


