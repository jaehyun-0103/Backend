from django.urls import path
from .views import GreatsList

urlpatterns = [
    path('', GreatsList.as_view(), name='greats_list'),
]