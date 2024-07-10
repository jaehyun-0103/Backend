# chat/urls.py
from django.urls import path
from .views import ChatTemplateView, TalkView

urlpatterns = [
    path('', ChatTemplateView.as_view(), name='chat'),  # HTML 템플릿 뷰
    path('<int:story_id>/talk/', TalkView.as_view(), name='talk_api'),  # DRF API 뷰
]
