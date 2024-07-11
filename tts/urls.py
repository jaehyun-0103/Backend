#tts/urls.py
from django.urls import path
from .views import ChangeSoundView, GetTTSTaskView

urlpatterns = [
    path('change_sound/', ChangeSoundView.as_view(), name='change_sound'),
    path('get_tts_task/<str:task_id>/', GetTTSTaskView.as_view(), name='get_tts_task'),
]
