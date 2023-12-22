from django.urls import path
from .views import *
urlpatterns = [
    path('register/', register_view),
    path('active_user/', active_user),
    path('login/', login_view),
    path('get_messages/', get_messages),
    path('get_histories/', get_histories),
    path('get_favorites/', get_favorites),
    path('get_follows/', get_follows),
    path('follow_scholar/', follow_scholar),
    path('unfollow_scholar/', unfollow_scholar),
    path('get_user_info/', get_user_info),
    path('add_favorite/', add_favorite),
    path('remove_favorite/', remove_favorite),
    path('record_history/', record_history),
    path('add_focus_concept/', add_focus_concept),
    path('remove_focus_concept/', remove_focus_concept),
    path('get_focus_concepts/', get_focus_concepts),
    path('clear_histories/', clear_histories),
    path('change_user_info/', change_user_info),
    path('check_concept_focus/', check_concept_focus),
    path('upload_user_avatar/', upload_user_avatar),
    path('get_user_avatar/', get_user_avatar),
    path('check_author_follow/', check_author_follow),
    path('apply_for_certification/', apply_for_certification),
    path('relieve_certification/', relieve_certification),
    path('get_certification_status/', get_certification_status),
    path('apply_for_complaint/', apply_for_complaint),
    path('get_messages_all/', get_messages_all),
    path('test/', test),
]
