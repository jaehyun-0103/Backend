from django.urls import path
from .views import DateVisitsAPIView, AgeVisitsAPIView, ChatVisitsAPIView, CorrectRateAPIView

urlpatterns = [
    path('date-visits/', DateVisitsAPIView.as_view(), name='date_visits'),
    path('age-visits/', AgeVisitsAPIView.as_view(), name='age_visits'),
    path('chat-visits/', ChatVisitsAPIView.as_view(), name='chat_visits'),
    path('correct-rate/', CorrectRateAPIView.as_view(), name='correct_rate'),
]