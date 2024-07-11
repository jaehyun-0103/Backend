# tts/tasks.py
import requests
from django.conf import settings
from celery import shared_task
from django.http import HttpResponse

NAVER_CLOVA_TTS_API_URL = 'https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts'

@shared_task
def convert_text_to_speech(text):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-NCP-APIGW-API-KEY-ID': settings.NAVER_CLIENT_ID,
        'X-NCP-APIGW-API-KEY': settings.NAVER_CLIENT_SECRET
    }
    data = {
        'speaker': 'mijin',  # 사용할 스피커 이름
        'speed': '0',  # 속도 (-5 ~ 5)
        'text': text
    }

    response = requests.post(NAVER_CLOVA_TTS_API_URL, headers=headers, data=data)
    response.raise_for_status()

    voice_data = response.content

    return voice_data
