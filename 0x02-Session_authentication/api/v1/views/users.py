#!/usr/bin/env python3
""" Module of Users views
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
import base64

@app_views.route('/users', methods=['GET'], strict_slashes=False)
def view_all_users() -> str:
    """ GET /api/v1/users
    Return:
      - list of all User objects JSON represented
    """
    if not authenticate():
        return jsonify({'error': 'Unauthorized'}), 401
    all_users = [user.to_json() for user in User.all()]
    return jsonify(all_users)


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
def view_one_user(user_id: str = None) -> str:
    """ GET /api/v1/users/:id
    Path parameter:
      - User ID
    Return:
      - User object JSON represented
      - 404 if the User ID doesn't exist
    """
    if not authenticate():
        return jsonify({'error': 'Unauthorized'}), 401
    if user_id is None:
        abort(404)
    user = User.get(user_id)
    if user is None:
        abort(404)
    return jsonify(user.to_json())


@app_views.route('/users/<user_id>', methods=['DELETE'], strict_slashes=False)
def delete_user(user_id: str = None) -> str:
    """ DELETE /api/v1/users/:id
    Path parameter:
      - User ID
    Return:
      - empty JSON if the User has been correctly deleted
      - 404 if the User ID doesn't exist
    """
    if not authenticate():
        return jsonify({'error': 'Unauthorized'}), 401
    if user_id is None:
        abort(404)
    user = User.get(user_id)
    if user is None:
        abort(404)
    user.remove()
    return jsonify({}), 200


@app_views.route('/users', methods=['POST'], strict_slashes=False)
def create_user() -> str:
    """ POST /api/v1/users/
    JSON body:
      - email
      - password
      - last_name (optional)
      - first_name (optional)
    Return:
      - User object JSON represented
      - 400 if can't create the new User
    """
    rj = None
    error_msg = None
    try:
        rj = request.get_json()
    except Exception:
        rj = None
    
    if rj is None:
        return jsonify({'error': 'Wrong format'}), 400
    
    email = rj.get('email', '')
    password = rj.get('password', '')
    
    if email == '':
        error_msg = 'email missing'
    elif password == '':
        error_msg = 'password missing'
    else:
        try:
            # Password hashing
            hashed_password = generate_password_hash(password)

            if error_msg is None:
                user = User()
                user.email = email
                user.password = hashed_password
                user.first_name = rj.get('first_name')
                user.last_name = rj.get('last_name')
                user.save()
                return jsonify(user.to_json()), 201
        except Exception as e:
            error_msg = f"Can't create User: {str(e)}"
    
    return jsonify({'error': error_msg}), 400


@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
def update_user(user_id: str = None) -> str:
    """ PUT /api/v1/users/:id
    Path parameter:
      - User ID
    JSON body:
      - last_name (optional)
      - first_name (optional)
    Return:
      - User object JSON represented
      - 404 if the User ID doesn't exist
      - 400 if can't update the User
    """
    if not authenticate():
        return jsonify({'error': 'Unauthorized'}), 401
    if user_id is None:
        abort(404)
    user = User.get(user_id)
    if user is None:
        abort(404)

    rj = None
    try:
        rj = request.get_json()
    except Exception:
        rj = None

    if rj is None:
        return jsonify({'error': 'Wrong format'}), 400

    if rj.get('first_name') is not None:
        user.first_name = rj.get('first_name')
    if rj.get('last_name') is not None:
        user.last_name = rj.get('last_name')

    try:
        user.save()
        return jsonify(user.to_json()), 200
    except Exception as e:
        return jsonify({'error': f"Can't update User: {str(e)}"}), 400


def authenticate() -> bool:
    """ Basic Authentication function """
    auth = request.headers.get('Authorization')
    if not auth:
        return False

    try:
        auth_type, auth_string = auth.split(' ')
        if auth_type != 'Basic':
            return False
        auth_decoded = base64.b64decode(auth_string).decode('utf-8')
        email, password = auth_decoded.split(':')
    except (ValueError, TypeError):
        return False

    # Here we would match against your user database, example:
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return True
    return False

