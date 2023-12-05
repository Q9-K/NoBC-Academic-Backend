from django.apps import AppConfig
from elasticsearch_dsl import connections

class PaperConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "work"