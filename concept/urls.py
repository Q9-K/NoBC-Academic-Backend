from .views import *
from django.urls import path
urlpatterns = [
    path('get_level_0/', get_level_0),
    path('get_tree/',get_tree),
    path('search_concept/',search_concept_by_keyword),
]