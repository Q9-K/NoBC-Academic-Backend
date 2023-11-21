from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import *


@registry.register_document
class ScholarDocument1(Document):
    class Index:
        name = 'paper1'
        settings = {
            'number_of_shards': 3,
            'number_of_replicas': 0
        }

    class Django:
        model = Paper1
        queryset_pagination = 50000
        fields = [
            'abstract',
        ]


@registry.register_document
class ScholarDocument2(Document):
    class Index:
        name = 'paper2'
        settings = {
            'number_of_shards': 3,
            'number_of_replicas': 0
        }

    class Django:
        model = Paper2
        queryset_pagination = 50000
        fields = [
            'abstract',
        ]


@registry.register_document
class ScholarDocument3(Document):
    class Index:
        name = 'paper3'
        settings = {
            'number_of_shards': 3,
            'number_of_replicas': 0
        }

    class Django:
        model = Paper3
        queryset_pagination = 50000
        fields = [
            'abstract',
        ]



@registry.register_document
class ScholarDocument4(Document):
    class Index:
        name = 'paper4'
        settings = {
            'number_of_shards': 3,
            'number_of_replicas': 0
        }

    class Django:
        model = Paper4
        queryset_pagination = 50000
        fields = [
            'abstract',
        ]


@registry.register_document
class ScholarDocument5(Document):
    class Index:
        name = 'paper5'
        settings = {
            'number_of_shards': 3,
            'number_of_replicas': 0
        }

    class Django:
        model = Paper5
        queryset_pagination = 50000
        fields = [
            'abstract',
        ]

@registry.register_document
class ScholarDocument6(Document):
    class Index:
        name = 'paper6'
        settings = {
            'number_of_shards': 3,
            'number_of_replicas': 0
        }

    class Django:
        model = Paper6
        queryset_pagination = 50000
        fields = [
            'abstract',
        ]


@registry.register_document
class ScholarDocument7(Document):
    class Index:
        name = 'paper7'
        settings = {
            'number_of_shards': 3,
            'number_of_replicas': 0
        }

    class Django:
        model = Paper7
        queryset_pagination = 50000
        fields = [
            'abstract',
        ]


@registry.register_document
class ScholarDocument8(Document):
    class Index:
        name = 'paper8'
        settings = {
            'number_of_shards': 3,
            'number_of_replicas': 0
        }

    class Django:
        model = Paper8
        queryset_pagination = 50000
        fields = [
            'abstract',
        ]


@registry.register_document
class ScholarDocument9(Document):
    class Index:
        name = 'paper9'
        settings = {
            'number_of_shards': 3,
            'number_of_replicas': 0
        }

    class Django:
        model = Paper9
        queryset_pagination = 50000
        fields = [
            'abstract',
        ]

@registry.register_document
class ScholarDocument10(Document):
    class Index:
        name = 'paper10'
        settings = {
            'number_of_shards': 3,
            'number_of_replicas': 0
        }

    class Django:
        model = Paper10
        queryset_pagination = 50000
        fields = [
            'abstract',
        ]