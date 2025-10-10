from flask import Blueprint, request, jsonify
from config import get_db_connection
from utils.jwt_handler import verify_token

history_bp = Blueprint('history', __name__, url_prefix='/history')

def get_user_id_from_token():
    """Extract user_id from JWT token in Authorization header."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return None

    return payload.get('user_id')

@history_bp.route('/add', methods=['POST'])
def add_history():
    """Add a scan result to user's history."""
    try:
        # Decode JWT to get user_id
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'error': 'Valid JWT token required'}), 401

        data = request.get_json()

        # Validate input
        if not data or not data.get('url') or not data.get('result'):
            return jsonify({'error': 'URL and result are required'}), 400

        url = data['url'].strip()
        result = data['result']

        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400

        if result not in ['safe', 'unsafe']:
            return jsonify({'error': 'Result must be either "safe" or "unsafe"'}), 400

        # Save record into history table with timestamp
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO history (user_id, url, result) VALUES (?, ?, ?)',
            (user_id, url, result)
        )
        conn.commit()
        scan_id = cursor.lastrowid
        conn.close()

        return jsonify({'message': 'Scan added to history successfully'}), 201

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@history_bp.route('', methods=['GET'])
def get_history():
    """Get scan history for the logged-in user."""
    try:
        # Decode JWT to get user_id
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'error': 'Valid JWT token required'}), 401

        # Return list of scan records for the user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, url, result, timestamp FROM history WHERE user_id = ? ORDER BY timestamp DESC',
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        history_list = []
        for row in rows:
            history_list.append({
                'id': row['id'],
                'url': row['url'],
                'result': row['result'],
                'timestamp': row['timestamp']
            })

        return jsonify(history_list), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
