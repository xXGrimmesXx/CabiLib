import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Scopes used by the application
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.compose',
]

# Module-level caches for credentials and built service clients
_CREDS = None
_SERVICE_CACHE = {}


def validate_token():
    """Validate or obtain OAuth2 credentials and cache them in module state."""
    global _CREDS
    if _CREDS is not None and _CREDS.valid:
        return _CREDS

    creds = None
    token_path = 'src/token.json'
    creds_path = 'src/credentials.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    _CREDS = creds
    return _CREDS


def get_service(api_name, api_version):
    """Return a cached google-api service client for (api_name, api_version).

    This avoids recreating service objects and centralises credential handling.
    """
    key = (api_name, api_version)
    service = _SERVICE_CACHE.get(key)
    if service is not None:
        return service

    creds = validate_token()
    service = build(api_name, api_version, credentials=creds)
    _SERVICE_CACHE[key] = service
    return service


def get_gmailV1_service():
    """Convenience wrapper for Gmail v1 service."""
    return get_service('gmail', 'v1')

def get_calendarV3_service():
    """Convenience wrapper for Calendar v3 service."""
    return get_service('calendar', 'v3')