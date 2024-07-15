#tts/views.py
import os
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from .tasks import process_tts
from django.core.files.storage import default_storage

class ChangeSoundView(APIView):
    def post(self, request):
        sentence = request.data.get('sentence')

        if not sentence:
            return Response({"error": "Sentence is required"}, status=status.HTTP_400_BAD_REQUEST)

        task = process_tts.delay(sentence)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class GetAudioResultView(APIView):
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