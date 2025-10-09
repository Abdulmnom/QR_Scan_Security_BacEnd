import requests
from config import Config

def check_url_safety(url):
    api_key = Config.GOOGLE_SAFE_BROWSING_KEY

    if not api_key:
        return {
            'status': 'error',
            'message': 'Google Safe Browsing API key not configured'
        }

    api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}'

    payload = {
        'client': {
            'clientId': 'secure-qr-scanner',
            'clientVersion': '1.0.0'
        },
        'threatInfo': {
            'threatTypes': [
                'MALWARE',
                'SOCIAL_ENGINEERING',
                'UNWANTED_SOFTWARE',
                'POTENTIALLY_HARMFUL_APPLICATION'
            ],
            'platformTypes': ['ANY_PLATFORM'],
            'threatEntryTypes': ['URL'],
            'threatEntries': [
                {'url': url}
            ]
        }
    }

    try:
        response = requests.post(api_url, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()

            if result.get('matches'):
                return {
                    'status': 'unsafe',
                    'threats': [match['threatType'] for match in result['matches']]
                }
            else:
                return {'status': 'safe'}
        else:
            return {
                'status': 'error',
                'message': f'API returned status code {response.status_code}'
            }

    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'Request failed: {str(e)}'
        }
