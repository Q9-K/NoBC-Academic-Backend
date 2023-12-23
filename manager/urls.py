from django.urls import path
from .views import *


urlpatterns = [
    path('login/', login),
    path('get_certifications_pending/', get_certifications_pending),
    path('get_certifications_all/', get_certifications_all),
    path('get_complaints_pending/', get_complaints_pending),
    path('get_complaints_all/', get_complaints_all),
    path('check_certification/', check_certification),
    path('check_complaint/', check_complaint),
    path('get_certification_detail/', get_certification_detail),
    path('get_complaint_detail/', get_complaint_detail),
    path('get_user_info_by_email/',get_user_info_by_email),
    path('get_user_avatar_by_email/', get_user_avatar_by_email)

]
