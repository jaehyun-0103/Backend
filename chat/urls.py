#chat/urls.py
from django.urls import path
from .views import ChatTemplateView, TalkView

urlpatterns = [
    path('<int:story_id>/talk/', ChatTemplateView.as_view(), name='chat'),  # HTML 템플릿 뷰
    path('<int:story_id>/', TalkView.as_view(), name='talk'),    # DRF API 뷰
]
