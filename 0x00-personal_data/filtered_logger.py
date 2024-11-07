#!/usr/bin/env python3
"""
Main file
"""

import re


def filter_datum(fields, redaction, message, separator):
    """
    Returns the log message with specified fields obfuscated.

    Args:
        fields (list): List of strings representing all fields to obfuscate.
        redaction (str): String to replace the field value.
        message (str): The log line.
        separator (str): Character separating fields in the log line.

    Returns:
        str: The obfuscated log message.
    """
    pattern = f'({"|".join(fields)})=[^;]*'
    return re.sub(pattern, lambda x: x.group().split('=')[0] + '=' + redaction, message)


if __name__ == "__main__":
    fields = ["password", "date_of_birth"]
    messages = [
        "name=egg;email=eggmin@eggsample.com;password=eggcellent;date_of_birth=12/12/1986;",
        "name=bob;email=bob@dylan.com;password=bobbycool;date_of_birth=03/04/1993;"
    ]

    for message in messages:
        print(filter_datum(fields, 'xxx', message, ';'))

