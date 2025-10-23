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

@history_bp.route('/<int:history_id>', methods=['DELETE'])
def delete_history_item(history_id):
    """Delete a specific history item by ID."""
    try:
        # Decode JWT to get user_id
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'error': 'Valid JWT token required'}), 401

        # Check if the history item exists and belongs to the user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id FROM history WHERE id = ? AND user_id = ?',
            (history_id, user_id)
        )
        item = cursor.fetchone()

        if not item:
            conn.close()
            return jsonify({'error': 'History item not found or access denied'}), 404

        # Delete the history item
        cursor.execute('DELETE FROM history WHERE id = ?', (history_id,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'History item deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@history_bp.route('', methods=['DELETE'])
def clear_all_history():
    """Delete all history items for the authenticated user."""
    try:
        # Decode JWT to get user_id
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'error': 'Valid JWT token required'}), 401

        # Delete all history items for the user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history WHERE user_id = ?', (user_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return jsonify({
            'message': f'All history items deleted successfully',
            'deleted_count': deleted_count
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@history_bp.route('', methods=['GET', 'POST'])
def get_history():
    """Get scan history for the logged-in user or add new history item."""
    # Handle POST request for adding history
    if request.method == 'POST':
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

            if result not in ['safe', 'trusted', 'unsafe']:
                return jsonify({'error': 'Result must be either "safe", "trusted", or "unsafe"'}), 400

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

    # Handle GET request for retrieving history
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
