from sqlalchemy import Column, Integer, String, func, Date, DateTime
from sqlalchemy.orm import declarative_base, relationship



Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    surname = Column(String(50), nullable=False, index=True)
    email = Column(String(100), unique=True, index=True)
    mobile = Column(Integer, nullable=True)
    date_of_birth = Column(Date)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

