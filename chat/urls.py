#chat/urls.py
from django.urls import path
from .views import ChatTemplateView, GPTChatView

urlpatterns = [
    path('<int:story_id>/talk/', ChatTemplateView.as_view(), name='chat'),  # HTML 템플릿 뷰
    path('<int:story_id>/', GPTChatView.as_view(), name='gptchat'),    # DRF API 뷰
]
