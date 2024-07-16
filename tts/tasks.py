# tts/tasks.py
import os
import requests
from django.conf import settings
from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


@shared_task
def process_tts(sentence):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"

    payload = {
        "text": sentence,
        "model_id": settings.ELEVENLABS_MODEL_ID,
        "voice_settings": {
            "stability": 0.50,
            "similarity_boost": 0.02,
            "style": 0.90,
            "use_speaker_boost": True
        }
    }

    headers = {
        "Content-Type": "application/json",
        "xi-api-key": settings.ELEVENLABS_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    response.raise_for_status()

    voice_data = response.content

    file_name = f"tts_output_{sentence[:10]}.mp3"
    file_path = default_storage.save(file_name, ContentFile(voice_data))

    return file_path

