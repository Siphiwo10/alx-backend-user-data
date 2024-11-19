#!/usr/bin/env python3

"""API Routes Module"""

from flask import Flask, jsonify, request, abort, redirect, make_response
from db import DB
from auth import Auth
from user import User

# Initialize Auth and Flask app
auth = Auth()
app = Flask(__name__)


@app.route('/', methods=['GET'], strict_slashes=False)
def home() -> str:
    """
    Welcome route
    Returns:
        A JSON welcome message
    """
    return jsonify({"message": "Welcome"})


@app.route('/users', methods=['POST'], strict_slashes=False)
def register_user() -> str:
    """
    User registration route
    Expects:
        - email: User email
        - password: User password
    Returns:
        JSON response with user info or an error message
    """
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        user = auth.register_user(email, password)
        return jsonify({"email": user.email, "message": "User successfully registered"})
    except ValueError:
        return jsonify({"message": "Email already exists"}), 400


@app.route('/sessions', methods=['POST'], strict_slashes=False)
def create_session() -> str:
    """
    Login route
    Expects:
        - email: User email
        - password: User password
    Returns:
        A response with a session ID cookie or an error message
    """
    email = request.form.get('email')
    password = request.form.get('password')
    if not auth.valid_login(email, password):
        abort(401)

    session_id = auth.create_session(email)
    response = make_response(jsonify({"email": email, "message": "Login successful"}))
    response.set_cookie('session_id', session_id)
    return response


@app.route('/sessions', methods=['DELETE'], strict_slashes=False)
def end_session() -> str:
    """
    Logout route
    Deletes session and redirects to home
    """
    session_id = request.cookies.get("session_id")
    user = auth.get_user_from_session_id(session_id)

    if not session_id or not user:
        abort(403)

    auth.destroy_session(user.id)
    return redirect('/')


@app.route('/profile', methods=['GET'], strict_slashes=False)
def get_profile() -> str:
    """
    User profile route
    Returns:
        - Email of the authenticated user
        - 403 if session is invalid
    """
    session_id = request.cookies.get("session_id")
    user = auth.get_user_from_session_id(session_id)

    if not session_id or not user:
        abort(403)

    return jsonify({"email": user.email})


@app.route('/reset_password', methods=['POST'], strict_slashes=False)
def request_password_reset() -> str:
    """
    Password reset token request
    Expects:
        - email: User email
    Returns:
        A reset token for the user
    """
    email = request.form.get('email')
    try:
        token = auth.get_reset_password_token(email)
        return jsonify({"email": email, "reset_token": token})
    except ValueError:
        abort(403)


@app.route('/reset_password', methods=['PUT'], strict_slashes=False)
def reset_password() -> str:
    """
    Update password route
    Expects:
        - email: User email
        - reset_token: Reset token
        - new_password: New password
    Returns:
        A success message or 403 if the token is invalid
    """
    email = request.form.get('email')
    token = request.form.get('reset_token')
    new_password = request.form.get('new_password')

    try:
        auth.update_password(token, new_password)
        return jsonify({"email": email, "message": "Password updated successfully"})
    except Exception:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

