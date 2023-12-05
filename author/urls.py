from .views import *
from django.urls import path
urlpatterns = [
    path('common_search/', common_search),
    path('get_works/', get_works),
]
