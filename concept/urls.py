from .views import *
from django.urls import path

urlpatterns = [
    path('get_level_0/', get_level_0),
    path('get_subdomains/', get_subdomains),
    path('search_concept/', search_concept_by_keyword),
    path('get_concept_by_id/', get_concept_by_id),
    path('get_popular_field/', get_hot_concepts),
    path('get_works_by_id/', search_works_by_concept),
    path('get_ancestors_by_id/',get_ancestor_concepts),
    path('get_works_by_focused_concept/', get_works_with_followed_concepts),
]
