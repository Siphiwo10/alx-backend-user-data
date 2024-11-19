#!/usr/bin/env python3

"""Database class for managing and updating user data."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from user import Base, User


class DB:
    """Handles interactions with the user database."""

    def __init__(self):
        """Sets up the database engine and initializes the schema."""
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)  # Clears any existing tables
        Base.metadata.create_all(self._engine)  # Creates new tables
        self.__session = None

    @property
    def _session(self):
        """
        Provides a session for interacting with the database.
        Creates one if it does not already exist.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Adds a new user to the database and saves the changes.
        Returns:
            User: The newly created user object.
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """
        Searches for a user using specific filters.
        Raises:
            InvalidRequestError: If an invalid attribute is provided.
            NoResultFound: If no matching user is found.
        Returns:
            User: The matching user object.
        """
        valid_keys = [
            'id',
            'email',
            'hashed_password',
            'session_id',
            'reset_token'
        ]

        for key in kwargs.keys():
            if key not in valid_keys:
                raise InvalidRequestError

        user = self._session.query(User).filter_by(**kwargs).first()
        if user is None:
            raise NoResultFound
        return user

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Updates attributes of a specific user and commits changes.
        Raises:
            ValueError: If an invalid attribute is provided.
        """
        user_to_update = self.find_user_by(id=user_id)

        valid_keys = [
            'id',
            'email',
            'hashed_password',
            'session_id',
            'reset_token'
        ]

        for key, value in kwargs.items():
            if key in valid_keys:
                setattr(user_to_update, key, value)
            else:
                raise ValueError

        self._session.commit()
