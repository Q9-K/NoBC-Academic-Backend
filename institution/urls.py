from .views import *
from django.urls import path
urlpatterns = [
    path("getInstitutionList/", getInstitutionList, name="getInstitutionList"),
    path("getInstitutionDetail/", getInstitutionDetail, name="getInstitutionDetail"),
    path("getInstitutionByKeyword/", getInstitutionByKeyword, name="getInstitutionByKeyword"),
]