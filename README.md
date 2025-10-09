# Secure QR Code Scanning Backend

A Python Flask backend for scanning QR code links for phishing or malicious content using Google Safe Browsing API.

## Features

- User authentication with JWT tokens
- QR code URL scanning using Google Safe Browsing API
- Scan history management per user
- SQLite local database storage
- Password hashing with bcrypt

## Project Structure

```
secure_qr_backend/
├── app.py                     # Entry point
├── config.py                  # Configuration settings
├── requirements.txt           # Dependencies
├── database/
│   └── db.sqlite3             # SQLite database
├── routes/
│   ├── auth_routes.py         # Authentication endpoints
│   ├── scan_routes.py         # URL scanning endpoint
│   └── history_routes.py      # History management endpoints
├── models/
│   ├── user_model.py          # User database model
│   └── history_model.py       # History database model
└── utils/
    ├── verify_link.py         # Google Safe Browsing API integration
    └── jwt_handler.py         # JWT token handling
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Add your Google Safe Browsing API key to `.env`:
```
GOOGLE_SAFE_BROWSING_KEY=your_api_key_here
JWT_SECRET_KEY=your_secret_key_here
```

## Running the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication

#### POST /auth/signup
Register a new user
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

#### POST /auth/login
Login existing user
```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```

### Scanning

#### POST /scan
Scan a URL for threats (no authentication required)
```json
{
  "url": "https://example.com"
}
```

Response:
```json
{
  "status": "safe",
  "url": "https://example.com",
  "threats": []
}
```

### History (Requires Authentication)

#### GET /history
Get scan history for logged-in user
```
Headers: Authorization: Bearer <token>
```

#### POST /history/add
Add a scan to user's history
```json
Headers: Authorization: Bearer <token>
{
  "url": "https://example.com",
  "result": "safe"
}
```

## Security Features

- Passwords are hashed using bcrypt
- JWT tokens for secure authentication
- Protected routes require valid tokens
- SQLite database with proper foreign key constraints

## Google Safe Browsing API

Get your API key from: https://developers.google.com/safe-browsing/v4/get-started

The API checks URLs against Google's lists of unsafe web resources including:
- Malware
- Social engineering (phishing)
- Unwanted software
- Potentially harmful applications
