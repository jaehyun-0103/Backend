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
            "similarity_boost": 0.05,
            "style": 0.90,
            "use_speaker_boost": True
        }
    }

    headers = {
        "Content-Type": "application/json",
        "xi-api-key": settings.ELEVENLABS_API_KEY
    }


    #만들기에서 그치지 말고 s3에 저장해야됨.
    #post하면 s3에 저장할 수 있도록. s3filename이 나옴. 이것 가지고 url가지고 그걸 바로 result해서 프론트에 보내는 방식.
    #post했을 때 s3 url을 한번에 주는게 어떨까.
    #task id를 리턴하지 말고, post요청 안에서 voice를 생성하고, 그 보이스 데이터를 s3에 업로드까지 구현해보기.
    #return값으로 url이 나오도록.

    response = requests.post(url, json=payload, headers=headers)
    #s3에 저장 후 url넘겨주기

    response.raise_for_status()

    voice_data = response.content

    file_name = f"tts_output_{sentence[:10]}.mp3"
    file_path = default_storage.save(file_name, ContentFile(voice_data))


    return file_path

