from .views import *
from django.urls import path

urlpatterns = [
    path('get_source_by_id/', get_source_by_id),
    path('get_source_list/', get_source_list),
    path('get_hot_sources/', get_hot_sources),
    path('get_works_by_cited/', get_works_by_cited),
    path('get_authors_by_cited/', get_authors_by_cited),
    path('get_authors_distribution/', get_authors_distribution),
    path('search_sources/', search_sources),
    path('get_latest_sources/', get_latest_sources),
    path('get_sources_by_concept/', get_sources_by_concept),
]