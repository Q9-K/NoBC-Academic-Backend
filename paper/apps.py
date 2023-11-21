from django.apps import AppConfig
from elasticsearch_dsl import connections

class PaperConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "paper"

    def ready(self):
        connections.create_connection(hosts=['localhost'])
