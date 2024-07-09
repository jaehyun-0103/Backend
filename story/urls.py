from django.urls import path
from .views import GreatsList, GreatDetail, IncrementAccessCount

urlpatterns = [
    path('', GreatsList.as_view(), name='greats_list'),
    path('<int:story_id>/', GreatDetail.as_view(), name='great_detail'),
    path('<int:story_id>/talk/', IncrementAccessCount.as_view(), name='increment_access_count'),
]