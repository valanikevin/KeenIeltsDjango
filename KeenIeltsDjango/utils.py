from django.conf import settings
from config import DEBUG


def imgix_url(url, complete=True):
    if DEBUG:
        if complete:
            return f'{settings.BASE_URL}{url}'
        else:
            return url
    else:
        return 'https://keenielts-django.imgix.net/' + url
