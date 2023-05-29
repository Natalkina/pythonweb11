from sqlalchemy import Column, Integer, DateTime, String, func, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    surname = Column(String(50), nullable=False, index=True)
    email = Column(String(100), unique=True, index=True)
    mobile = Column(String, nullable=True, index=True)
    date_of_birth = Column(Date)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref='contacts')

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)


