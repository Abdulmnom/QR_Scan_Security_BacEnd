from flask import Blueprint, request, jsonify
from utils.verify_link import verify_link
from utils.qr_processor import extract_qr_from_image
from utils.jwt_handler import verify_token
from config import get_db_connection

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
        elif result['status'] == 'trusted':
            return jsonify({
                'status': 'trusted',
                'message': 'Site appears trustworthy'
            }), 200
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

@scan_bp.route('/scan/image', methods=['POST'])
def scan_image():
    """Scan QR code from uploaded image and check URL safety."""
    try:
        # Check if image file is provided
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        # Extract QR code from image
        qr_data = extract_qr_from_image(file)

        if not qr_data:
            return jsonify({'error': 'No QR code found in image'}), 400

        # Check URL safety using existing verify_link function
        result = verify_link(qr_data)

        # Save to history if user is authenticated
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if payload:
                user_id = payload.get('user_id')
                # Save scan result to history
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO history (user_id, url, result) VALUES (?, ?, ?)',
                    (user_id, qr_data, result['status'])
                )
                conn.commit()
                conn.close()

        # Return response
        response_data = {
            'url': qr_data,
            'status': result['status']
        }

        if result['status'] == 'unsafe':
            response_data['threats'] = result.get('threats', [])
        elif result['status'] == 'trusted':
            response_data['message'] = 'Site appears trustworthy'

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error in scan_image: {e}")
        return jsonify({'error': 'Internal server error'}), 500
