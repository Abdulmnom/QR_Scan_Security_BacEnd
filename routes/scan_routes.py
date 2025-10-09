from flask import Blueprint, request, jsonify
from utils.verify_link import check_url_safety

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/scan', methods=['POST'])
def scan_url():
    data = request.get_json()

    if not data or not data.get('url'):
        return jsonify({'error': 'URL is required'}), 400

    url = data['url']

    result = check_url_safety(url)

    if result['status'] == 'error':
        return jsonify({
            'error': result['message']
        }), 500

    return jsonify({
        'status': result['status'],
        'url': url,
        'threats': result.get('threats', [])
    }), 200
