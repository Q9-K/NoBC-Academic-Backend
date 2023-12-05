from .views import *
from django.urls import path
urlpatterns = [
    path('get_author_by_name/', get_author_by_name),
    path('get_author_by_id/', get_author_by_id),
    path('get_works/', get_works),
    path('get_hot_authors/', get_hot_authors),
    path('get_related_authors/', get_related_authors),
    path('get_scholar_metrics/', get_scholar_metrics),
]
