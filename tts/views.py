#tts/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import convert_text_to_speech
from django.http import HttpResponse

class ChangeSoundView(APIView):
    def post(self, request, *args, **kwargs):
        sentence = request.data.get('sentence')
        if not sentence:
            return Response({'error': 'Sentence is required'}, status=status.HTTP_400_BAD_REQUEST)
        #비동기로 tts변환 작업을 Celery에 전달

        #tts 변환 작업 시작
        task = convert_text_to_speech.delay(sentence)

        #task_id반환
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetTTSTaskView(APIView):
    def get(self, request, task_id, *args, **kwargs):
        # Celery 작업의 결과를 기다림
        result = convert_text_to_speech.AsyncResult(task_id)

        if result.ready():
            # 작업이 완료되었으면, 음성 데이터를 반환
            voice_data = result.result
            return HttpResponse(voice_data, content_type='audio/mpeg')
        else:
            # 작업이 아직 완료되지 않았으면, 적절한 응답 반환
            return Response({"error": "Task not found or not yet completed"}, status=status.HTTP_404_NOT_FOUND)


