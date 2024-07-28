DEBUG = True
CSRF_TRUSTED_ORIGINS = ['https://api.keenielts.com']
ALLOWED_HOSTS = ["*"]
BASE_URL = "http://192.168.10.55:8000"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''  # SMTP server
EMAIL_USE_TLS = True  # Use TLS
EMAIL_PORT = 587  # SMTP port
EMAIL_HOST_USER = ''  # Your SMTP username
EMAIL_HOST_PASSWORD = ''  # Your SMTP password
DEFAULT_FROM_EMAIL = ''  # Default 'from' email address

CORS_ALLOW_ALL_ORIGINS = DEBUG

SECRET_KEY = '@mu9#nsn6%ne@4gkxpv0z_jz^4f5e9&2(yan&4*gw1-hh4^#e+'
OPENAI_SECRET = ''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost'
    }
}

