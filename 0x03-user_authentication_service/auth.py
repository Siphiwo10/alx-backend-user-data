#!/usr/bin/env python3

"""Auth class for managing user data and authentication tasks."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from db import DB
from user import User
import bcrypt
import uuid


def _hash_password(password: str) -> str:
    """Generates a hashed and salted version of the provided password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def _generate_uuid() -> str:
    """Creates a new UUID and returns it as a string."""
    return str(uuid.uuid4())


class Auth:
    """Handles user authentication and interactions with the database."""

    def __init__(self):
        """Initializes the database connection for authentication operations."""
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Registers a new user.
        Raises:
            ValueError: If the email is already registered.
        Returns:
            User: The newly created user.
        """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists.")
        except NoResultFound:
            hashed_password = _hash_password(password)
            return self._db.add_user(email, hashed_password)

    def valid_login(self, email: str, password: str) -> bool:
        """
        Verifies login credentials by matching the password with its hash.
        Returns:
            bool: True if the login is valid, False otherwise.
        """
        try:
            user = self._db.find_user_by(email=email)
            return bcrypt.checkpw(password.encode('utf-8'), user.hashed_password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """
        Creates a new session for the user.
        Returns:
            str: The session ID, or None if the user is not found.
        """
        session_id = _generate_uuid()
        try:
            user = self._db.find_user_by(email=email)
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> str:
        """
        Retrieves the email of the user associated with the given session ID.
        Returns:
            str: The user's email, or None if no user is found.
        """
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user.email
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """
        Ends a user's session by setting their session ID to None.
        """
        try:
            user = self._db.find_user_by(id=user_id)
            self._db.update_user(user.id, session_id=None)
        except NoResultFound:
            pass

    def get_reset_password_token(self, email: str) -> str:
        """
        Generates a password reset token for the specified email.
        Raises:
            ValueError: If the email is not associated with a user.
        Returns:
            str: The reset token.
        """
        reset_token = _generate_uuid()
        try:
            user = self._db.find_user_by(email=email)
            self._db.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Updates the password of a user identified by a reset token.
        Raises:
            ValueError: If the reset token is invalid.
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError

        hashed_password = _hash_password(password)
        self._db.update_user(user.id, hashed_password=hashed_password, reset_token=None)
