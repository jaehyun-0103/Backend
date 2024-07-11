#backend/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Django의 기본 settings 모듈을 Celery의 기본으로 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
