#tts/views.py
import os
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from .tasks import process_tts
from django.core.files.storage import default_storage
from .serializers import TtsRequestSerializer
from rest_framework.decorators import api_view

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class ChangeSoundView(APIView):
    @swagger_auto_schema(
        operation_id="TTS변환하기",
        operation_description="celery로 텍스트 고유의 task_id생성",
        request_body=TtsRequestSerializer,
        responses={
            status.HTTP_202_ACCEPTED: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'task_id': openapi.Schema(type=openapi.TYPE_STRING, description='생성된 TTS 작업의 고유 task_id')
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='에러 메시지')
                }
            )
        }
    )
    def post(self, request):
        sentence = request.data.get('sentence')

        if not sentence:
            return Response({"error": "Sentence is required"}, status=status.HTTP_400_BAD_REQUEST)

        task = process_tts.delay(sentence)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class GetAudioResultView(APIView):
    @swagger_auto_schema(
        operation_id="TTS 결과 가져오기",
        operation_description="elevenlabs의 TTS API를 통해 변환된 mp3 파일 생성 및 반환하기",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="성공적으로 생성된 mp3 파일",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_BINARY,
                    description='audio/mpeg'
                ),
                headers={
                    'Content-Disposition': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='attachment; filename="tts_output_{sentence[:10]}.mp3"'
                    )
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='에러 메시지')
                }
            ),

        }
    )
    def get(self, request, task_id, *args, **kwargs):
        # Celery 작업의 결과를 기다림
        result = process_tts.AsyncResult(task_id)


        if result.ready():
            file_path = result.result

            if default_storage.exists(file_path):
                with default_storage.open(file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='audio/mpeg')
                    response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
                    return response

            else:
                return Response({"error": "파일을 찾을 수 없습니다."}, status = status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "결과가 아직 준비되지 않았습니다"}, status = status.HTTP_202_ACCEPTED)