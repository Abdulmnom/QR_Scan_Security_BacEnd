from flask import Blueprint, request, jsonify
from functools import wraps
from models.history_model import History
from utils.jwt_handler import verify_token, get_token_from_header

history_bp = Blueprint('history', __name__, url_prefix='/history')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = get_token_from_header(auth_header)

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        payload = verify_token(token)

        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        request.user_id = payload['user_id']
        return f(*args, **kwargs)

    return decorated

@history_bp.route('', methods=['GET'])
@token_required
def get_history():
    user_id = request.user_id

    history_model = History()
    history = history_model.get_user_history(user_id)

    return jsonify({
        'history': history
    }), 200

@history_bp.route('/add', methods=['POST'])
@token_required
def add_history():
    user_id = request.user_id
    data = request.get_json()

    if not data or not data.get('url') or not data.get('result'):
        return jsonify({'error': 'URL and result are required'}), 400

    url = data['url']
    result = data['result']

    if result not in ['safe', 'unsafe']:
        return jsonify({'error': 'Result must be either "safe" or "unsafe"'}), 400

    history_model = History()
    scan_id = history_model.add_scan(user_id, url, result)

    return jsonify({
        'message': 'Scan added to history',
        'id': scan_id
    }), 201
