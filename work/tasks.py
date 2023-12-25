
from celery import shared_task
from django_redis import get_redis_connection
from elasticsearch_dsl import connections, UpdateByQuery
from django.core.cache import cache

elasticsearch_connection = connections.get_connection()
INDEX_NAME = 'work_optimized'


@shared_task
def update_es():
    redis_connection = get_redis_connection("default")
    # 因为django-redis会自动为键添加前缀
    keys_with_prefix = list(redis_connection.scan_iter(match='nobc:1:visit_*'))
    keys_with_prefix = [key.decode('utf-8') for key in keys_with_prefix]
    print(keys_with_prefix)
    for key in keys_with_prefix:
        key = key.split('_')[1]
        visit_set = cache.get('visit_' + key)
        update_by_query = UpdateByQuery(using=elasticsearch_connection, index=INDEX_NAME)
        update_by_query = update_by_query.filter('term', id=key)
        update_by_query = update_by_query.script(source="ctx._source.visit_count+={}".format(len(visit_set)),
                                                 lang='painless')
        update_by_query.execute()
        cache.delete('visit_' + key)
