from django.apps import AppConfig
from elasticsearch_dsl import connections

class AuthorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "author"
