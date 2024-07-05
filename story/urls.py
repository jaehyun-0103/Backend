from django.urls import path
from .views import GreatsList

urlpatterns = [
    path('<int:user_id>/', GreatsList.as_view(), name='greats_list'),
]