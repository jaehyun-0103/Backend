#chat/urls.py
from django.urls import path
from .views import ChatTemplateView

urlpatterns = [
    path('<int:story_id>/talk/', ChatTemplateView.as_view(), name='chat'),  # HTML 템플릿 뷰
]
