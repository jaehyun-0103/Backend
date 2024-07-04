from django.urls import path
from .views import GetQuizView, UpdateQuizResult

urlpatterns = [
    path('<int:user_id>/<int:story_id>/', GetQuizView.as_view(), name='get_quiz'),
    path('update/<int:user_id>/<int:story_id>/', UpdateQuizResult.as_view(), name='update_quiz_result'),
]
