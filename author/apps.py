from django.apps import AppConfig
from elasticsearch_dsl import connections
from config import ELAS_HOST

class AuthorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "author"

    def ready(self):
        connections.create_connection(hosts=['http://123.60.99.8:9200'])
