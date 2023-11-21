from django.urls import path
from .views import *


urlpatterns = [
    path('login/', login_view),
    path('get_certifications/', get_certifications),
    path('get_complaints/', get_complaints),
]
