from .views import *
from django.urls import path

urlpatterns = [
    path('search/', search),
    path('advanced_search/', advanced_search),
    path('get_popular_works/', get_popular_works),
    path('get_work/', get_work),
    path('get_suggestion/', get_suggestion),
    path('get_reply/', get_reply),
    path('get_quick_reply/', get_quick_reply)
]
