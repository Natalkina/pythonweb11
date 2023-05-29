from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:

    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email if it exists. If no such user exists,
    it returns None.

    :param email: str: Specify the type of data that is expected to be passed in
    :param db: Session: Pass the database session to the function
    :return: An object of type user or none

    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:

    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Specify the type of data that is expected to be passed into the function
    :param db: Session: Pass in the database session to be used for this function
    :return: A user object

    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError("Failed to create user", str(e))
    db.refresh(new_user)
    return new_user

async def update_token(user: User, token: str | None, db: Session) -> None:

    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user that is being updated
    :param token: str | None: Update the refresh token in the database
    :param db: Session: Pass the database session to the function
    :return: None

    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:

    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.

    :param email: str: Pass the email address of the user
    :param db: Session: Pass a database session to the function
    :return: None

    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:

    """
    The update_avatar function updates the avatar of a user in the database.

    :param email: Get the user from the database
    :param url: str: Specify the type of data that will be passed into the function
    :param db: Session: Pass the database session to the function
    :return: The user object

    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user

