from flask import Blueprint, request, jsonify
from utils.verify_link import verify_link

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/scan', methods=['POST'])
def scan_url():
    """Scan a URL for security threats."""
    try:
        data = request.get_json()

        # Validate input
        if not data or not data.get('url'):
            return jsonify({'error': 'URL is required'}), 400

        url = data['url'].strip()
        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400

        # Call helper to verify link
        result = verify_link(url)

        if result['status'] == 'safe':
            return jsonify({'status': 'safe'}), 200
        elif result['status'] == 'unsafe':
            return jsonify({
                'status': 'unsafe',
                'details': result.get('threats', [])
            }), 200
        else:
            # Error case
            return jsonify({'error': result.get('message', 'Unknown error')}), 500

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
