from django.urls import path
from .views import GetQuizView, UpdateQuizResult

urlpatterns = [
    path('<int:story_id>/', GetQuizView.as_view(), name='get_quiz'),
    path('<int:story_id>/puzzles/', UpdateQuizResult.as_view(), name='update_quiz_result'),
]
