from django.apps import AppConfig
from elasticsearch_dsl import connections
from config import ELAS_HOST

class ScholarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "author"
