from .settings import *
from .settings import USE_HTTPS

CORS_ALLOWED_ORIGINS = [
    'http://localhost',
    'http://localhost:8000',
    'http://localhost:3000',
    'https://backend.bitroxmining.com',
    'https://www.backend.bitroxmining.com',
]
CORS_ALLOW_CREDENTIALS = True

X_FRAME_OPTIONS = 'DENY'

# Only via HTTPS
if USE_HTTPS:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = int(os.environ.get('SECURE_SSL_REDIRECT', 0))
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = 'strict-origin'
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True

