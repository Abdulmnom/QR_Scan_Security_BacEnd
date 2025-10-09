from flask import Blueprint, request, jsonify
from models.user_model import User
from utils.jwt_handler import generate_token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Name, email, and password are required'}), 400

    name = data['name']
    email = data['email']
    password = data['password']

    user_model = User()
    user = user_model.create_user(name, email, password)

    if not user:
        return jsonify({'error': 'User with this email already exists'}), 409

    token = generate_token(user['id'], user['email'])

    return jsonify({
        'message': 'User created successfully',
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email']
    password = data['password']

    user_model = User()
    user = user_model.get_user_by_email(email)

    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user_model.verify_password(password, user['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = generate_token(user['id'], user['email'])

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    }), 200
