from django.urls import path
from .views import GreatsList, GreatDetail

urlpatterns = [
    path('', GreatsList.as_view(), name='greats_list'),
    path('<int:pk>/', GreatDetail.as_view(), name='great_detail'),
]