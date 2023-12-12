from .views import *
from django.urls import path

urlpatterns = [
    path('common_search/', common_search),
    path('get_sources_by_initial/', get_sources_by_initial),
    path('get_sources_by_concept/',get_sources_by_concept),
]