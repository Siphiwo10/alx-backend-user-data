#!/usr/bin/env python3
"""
password file
"""

import bcrypt


def hash_password(password: str) -> bytes:
    """
    password using bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


if __name__ == "__main__":
    password = "MyAmazingPassw0rd"
    print(hash_password(password).decode('utf-8'))
