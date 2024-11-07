#!/usr/bin/env python3
"""
This script filters personal information (PII) from log messages using regular
expressions and environmental variables. It retrieves data from a secure
database and logs it with redacted PII fields.
"""

import re
import logging
import os
import csv
from typing import List
import mysql.connector


class RedactingFormatter(logging.Formatter):
    """
    Formatter class for redacting PII fields in log messages.
    """
    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """
        Initializes the RedactingFormatter with a list of fields to redact.
        """
        self.fields = fields
        super().__init__(self.FORMAT)

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record by filtering values and redacting them.
        """
        result = super().format(record)
        return filter_datum(
            self.fields,
            self.REDACTION,
            result,
            self.SEPARATOR
        )


PII_FIELDS = ('name', 'email', 'password', 'ssn', 'phone')


def filter_datum(fields: List[str], redaction: str, message: str, separator: str) -> str:
    """
    Returns the log message with specified fields redacted.
    """
    for item in fields:
        message = re.sub(rf'{item}=[^;]*', f'{item}={redaction}', message)
    return message


def get_db():
    """
    Retrieves a database connection using credentials stored in environment variables.
    """
    username = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    password = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    database = os.getenv('PERSONAL_DATA_DB_NAME')

    return mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=database
    )


def create_user_data_logger() -> logging.Logger:
    """
    Creates and configures a logger specifically for user data processing.
    """
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    target_handler = logging.StreamHandler()
    target_handler.setLevel(logging.INFO)

    formatter = RedactingFormatter(PII_FIELDS)
    target_handler.setFormatter(formatter)

    logger.addHandler(target_handler)

    return logger


def main() -> None:
    """
    Connects to the database, retrieves user data, formats it, and logs it with redacted PII.
    """
    logger = create_user_data_logger()
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users;")
    for row in cursor:
        # Create a log message from row data
        fields = '; '.join([f"{key}={value}" for key, value in zip(PII_FIELDS, row)])
        logger.info(fields)

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
