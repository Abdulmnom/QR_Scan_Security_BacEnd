from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.scan_routes import scan_bp
from routes.history_routes import history_bp
from config import init_database
import os

app = Flask(__name__)
CORS(app)

os.makedirs('database', exist_ok=True)
init_database()  # Initialize database tables

app.register_blueprint(auth_bp)
app.register_blueprint(scan_bp)
app.register_blueprint(history_bp)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Secure QR Code Scanning API',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'signup': 'POST /auth/signup',
                'login': 'POST /auth/login',
                'profile': 'GET /auth/me (requires auth)'
            },
            'scan': {
                'scan_url': 'POST /scan'
            },
            'history': {
                'get_history': 'GET /history (requires auth)',
                'add_history': 'POST /history/add (requires auth)'
            }
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
