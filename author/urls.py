from .views import *
from django.urls import path
urlpatterns = [
    # path('search/', search_view),
    # path('search2/', search_view2),
    path('common_search/', common_search),
]
