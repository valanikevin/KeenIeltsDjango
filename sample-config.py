DEBUG = True
CSRF_TRUSTED_ORIGINS = ['https://api.keenielts.com']
ALLOWED_HOSTS = ["*"]
BASE_URL = "http://192.168.10.55:8000"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zeptomail.com'  # SMTP server
EMAIL_USE_TLS = True  # Use TLS
EMAIL_PORT = 587  # SMTP port
EMAIL_HOST_USER = 'emailapikey'  # Your SMTP username
EMAIL_HOST_PASSWORD = 'wSsVR60j/RXzX696zWelceo4mwxRBF/wEkR4iQaivSWpTfiTpsc4lxGbAFWgSfQYRWFuFTFGor59zEgE0TcMi9x/wwlVXiiF9mqRe1U4J3x17qnvhDzDW2lZlhOAJYsLxgxikmZnEc8k+g=='  # Your SMTP password
DEFAULT_FROM_EMAIL = 'zepto.keenielts.com'  # Default 'from' email address

CORS_ALLOW_ALL_ORIGINS = DEBUG
