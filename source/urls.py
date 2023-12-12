from .views import *
from django.urls import path

urlpatterns = [
    path('get_source_by_id/', get_source_by_id),
    path('get_sources_by_initial/', get_sources_by_initial),
    path('get_sources_by_concept/',get_sources_by_concept),
]