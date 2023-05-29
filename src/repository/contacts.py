from sqlalchemy import and_, or_, text
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactStatusUpdate


async def get_contacts(skip: int, limit: int, user: User, db: Session):
    """
    The get_contacts function returns a list of contacts for the user.

    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param user: User: Get the user_id from the database
    :param db: Session: Access the database
    :return: A list of contacts

    """
    contact = db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()
    return contact

async def get_contact_by_id(contact_id: int, user: User, db: Session):

    """
    The get_contact_by_id function returns a contact object from the database based on the id of that contact.

    :param contact_id: int: Specify the id of the contact to be returned
    :param user: User: Get the user_id from the user object
    :param db: Session: Access the database
    :return: The contact with the given id if it exists, otherwise none
    """

    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel,  user: User, db: Session) -> Contact:
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Get the data from the request body
    :param user: User: Get the user id from the token
    :param db: Session: Access the database
    :return: A contact object

    """

    contact = Contact(
            id=None,
            name=body.name,
            surname=body.surname,
            email=body.email,
            mobile=body.mobile,
            date_of_birth=body.date_of_birth,
            user_id=user.id
        )

    try:
        db.add(contact)
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError("Failed to create user", str(e))
    db.refresh(contact)

    return contact


async def update_contact(body: ContactModel, contact_id: int, user: User, db: Session) -> Contact | None:

    """
    The update_contact function updates a contact in the database.

    :param body: ContactModel: Pass the contact data to be updated
    :param contact_id: int: Identify the contact that we want to update
    :param user: User: Get the user id from the token
    :param db: Session: Access the database
    :return: The updated contact

    """
    contact = db.query(Contact).filter(and_(Contact.id==contact_id, Contact.user_id == user.id)).first()

    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.mobile = body.mobile
        contact.date_of_birth = body.date_of_birth
        db.commit()
    return contact


async def get_contacts_by(name: str | None, surname: str | None, email: str | None, user: User, db: Session):

    """
    The get_contacts_by function returns a list of contacts that match the given name, surname and email.
        If no contact is found, an empty list is returned.

    :param name: str | None: Filter the contacts by name
    :param surname: str | None: Filter the contacts by surname
    :param email: str | None: Filter the contacts by email
    :param user: User: Get the user_id of the current logged in user
    :param db: Session: Pass the database session to the function
    :return: A list of contacts that match the search criteria

    """
    contacts = db.query(Contact).filter(
        and_(
            or_(
                Contact.name == name,
                Contact.surname == surname,
                Contact.email == email
            ),
            Contact.user_id == user.id
        )
    )

    if name:
        contacts = contacts.filter(Contact.name.like(f"%{name}%"))
    if surname:
        contacts = contacts.filter(Contact.surname.like(f"%{surname}%"))
    if email:
        contacts = contacts.filter(Contact.email.like(f"%{email}%"))
    print(f"name: {name}, surname: {surname}, email: {email}")

    contact = contacts.all()
    return contact


async def get_contacts_birthdays(user: User, db: Session):

    """
    The get_contacts_birthdays function returns a list of contacts whose birthdays are within the next 7 days.

    :param user: User: Pass the user object to the function
    :param db: Session: Pass the database session to the function
    :return: A list of contacts who have birthdays in the next 7 days

    """
    query = text("SELECT * FROM contacts WHERE extract(month from date_of_birth) = extract(month from now() + interval '7 days') AND extract(day from date_of_birth) >= extract(day from now()) AND extract(day from date_of_birth) <= extract(day from now() + interval '7 days');")
    contacts = db.execute(query).fetchall()

    return contacts


async def remove_contact(contact_id: int, user: User, db: Session):

    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Specify the id of the contact to be removed
    :param user: User: Get the user id from the database
    :param db: Session: Pass the database session to the function
    :return: The contact that was removed

    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

    if contact:
        db.delete(contact)
        db.commit()
    return contact


