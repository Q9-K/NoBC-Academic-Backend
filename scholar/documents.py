from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Scholar1, Scholar2, Scholar


@registry.register_document
class ScholarDocument(Document):
    class Index:
        name = 'scholar'
        settings = {
            'number_of_shards': 5,
            'number_of_replicas': 0
        }

    class Django:
        model = Scholar1
        queryset_pagination = 50000
        fields = [
            'name',
        ]
