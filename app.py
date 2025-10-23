from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.scan_routes import scan_bp
from routes.history_routes import history_bp
from config import init_database
import os

app = Flask(__name__)

# إعداد CORS للسماح بنطاق الفرونت اند
CORS(app, origins=[
    "http://localhost:5173",  # تطوير محلي
    "https://secureqrscanner.netlify.app/",  # نطاق الفرونت اند
    "https://your-render-frontend-url.onrender.com"  # رابط Render للفرونت اند
])

# إنشاء مجلد database إذا لم يكن موجوداً
os.makedirs('database', exist_ok=True)

# تهيئة قاعدة البيانات
init_database()

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
                'scan_url': 'POST /scan',
                'scan_image': 'POST /scan/image (multipart/form-data)'
            },
            'history': {
                'get_history': 'GET /history (requires auth)',
                'add_history': 'POST /history or POST /history/add (requires auth)',
                'delete_history_item': 'DELETE /history/<id> (requires auth)',
                'clear_all_history': 'DELETE /history (requires auth)'
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
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
