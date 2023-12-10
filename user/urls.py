from django.urls import path
from .views import *
urlpatterns = [
    path('register/', register_view),
    path('active_user/', active_user),
    path('login/', login_view),
    path('focus/', get_concept_focus),
    path('get_messages/', get_messages),
    path('get_histories/', get_histories),
    path('get_favorites/', get_favorites),
    path('follow', follow_scholar),
]
