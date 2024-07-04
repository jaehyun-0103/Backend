from django.urls import path
from .views import AllGreatsList

urlpatterns = [
    path('greats/<int:user_id>/', AllGreatsList.as_view(), name='all_greats_list'),
]