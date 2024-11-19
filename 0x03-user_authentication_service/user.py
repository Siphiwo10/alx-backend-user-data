#!/usr/bin/env python3

"""User model definition for the database."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    Represents a user in the database.
    Attributes:
        id (int): Primary key, auto-incremented.
        email (str): Unique email of the user.
        hashed_password (str): Securely hashed user password.
        session_id (str): Optional session ID for user authentication.
        reset_token (str): Optional token for password reset functionality.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False, unique=True)
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250), nullable=True)
    reset_token = Column(String(250), nullable=True)
