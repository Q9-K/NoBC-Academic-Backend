from .views import *
from django.urls import path
urlpatterns = [
    path('get_level_0/', get_level_0),
    path('get_subdomains/',get_subdomains),
    path('search_concept/',search_concept_by_keyword),
    path('get_concept_by_id/',get_concept_by_id),
    path('get_popular_field/',get_hot_concepts),
]