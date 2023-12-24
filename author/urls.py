from .views import *
from django.urls import path
urlpatterns = [
    path('get_author_by_name/', get_author_by_name),
    path('get_author_by_id/', get_author_by_id),
    path('get_works/', get_works),
    path('get_hot_authors/', get_hot_authors),
    path('get_co_author_list/', get_co_author_list),
    path('get_scholar_metrics/', get_scholar_metrics),
    path('post_scholar_intro_information/', post_scholar_intro_information),
    path('get_scholar_intro_information/', get_scholar_intro_information),
    path('post_scholar_basic_information/', post_scholar_basic_information),
    path('post_scholar_avatar/', post_scholar_avatar),
    path('get_counts_by_year/', get_counts_by_year),
    path('get_recommend_author/', get_recommend_author)
]
