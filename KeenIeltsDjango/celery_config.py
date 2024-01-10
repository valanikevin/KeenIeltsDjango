from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KeenIeltsDjango.settings')

app = Celery('keenielts_celery')

# Using Redis as broker
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# For additional options, you can directly pass in the URL to the broker setting
# Example: 'redis://localhost:6379/0'
