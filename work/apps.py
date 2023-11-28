from django.apps import AppConfig
from elasticsearch_dsl import connections

class WorkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "work"

    def ready(self):
        connections.create_connection(hosts=['localhost'])