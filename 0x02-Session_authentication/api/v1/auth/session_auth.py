#!/usr/bin/env python3
"""
Session-based authentication with Flask app.
"""

from flask import Flask, request, abort
import os
import uuid


class Auth:
    """
    Base Auth class with session cookie retrieval.
    """

    def session_cookie(self, request=None):
        """
        Retrieves the session cookie from the request.
        Uses the environment variable SESSION_NAME to define cookie name.
        """
        if request is None:
            return None
        session_name = os.getenv("SESSION_NAME", "_my_session_id")
        return request.cookies.get(session_name)


class SessionAuth(Auth):
    """
    Session-based authentication class.
    Stores and retrieves session IDs for users.
    """

    user_id_by_session_id = {}

    def create_session(self, user_id: str = None) -> str:
        """
        Creates a session ID for a given user_id.
        Returns the session ID, or None if user_id is invalid.
        """
        if user_id is None or not isinstance(user_id, str):
            return None
        session_id = str(uuid.uuid4())
        self.user_id_by_session_id[session_id] = user_id
        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """
        Retrieves the user ID based on a session ID.
        Returns None if session_id is invalid or doesn't exist.
        """
        if session_id is None or not isinstance(session_id, str):
            return None
        return self.user_id_by_session_id.get(session_id)


# Flask application setup
app = Flask(__name__)
auth = SessionAuth()


@app.before_request
def before_request():
    """
    Runs before each request.
    Checks for session cookie or authorization header.
    """
    excluded_paths = ["/api/v1/auth_session/login/", "/api/v1/status"]
    if request.path not in excluded_paths:
        if auth.authorization_header(request) is None and \
                auth.session_cookie(request) is None:
            abort(401)


@app.route('/', methods=['GET'], strict_slashes=False)
def root_path():
    """
    Root path to retrieve the cookie value for debugging.
    """
    return "Cookie value: {}\n".format(auth.session_cookie(request))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("API_PORT", 5000)))
