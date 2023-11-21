from django.apps import AppConfig
from elasticsearch_dsl import connections

class ScholarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scholar"

    def ready(self):
        connections.create_connection(hosts=['localhost'])
