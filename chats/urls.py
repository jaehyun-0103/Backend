from django.urls import path
from .views import TalkView

urlpatterns = [
    path('<int:story_id>/talk/', TalkView.as_view(), name='talk'),
    # 다른 URL 패턴들
]
