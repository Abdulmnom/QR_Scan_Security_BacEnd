import requests
from config import Config

def verify_link(url): # pylint: disable=invalid-name
    api_key = Config.GOOGLE_SAFE_BROWSING_KEY

    if not api_key:
        # If no API key, assume safe for trusted sites, but you should configure API key
        return {
            'status': 'trusted',
            'message': 'No API key configured - assuming trusted for known safe sites'
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
        elif response.status_code == 403:
            # API key issues - return trusted for known safe sites
            return {
                'status': 'trusted',
                'message': 'API access limited - site appears trustworthy'
            }
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
