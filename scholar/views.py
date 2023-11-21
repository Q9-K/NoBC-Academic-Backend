import hashlib

# from celery.result import AsyncResult
from django.http import JsonResponse
from django.core.cache import cache
from .tasks import sort_and_cache_results
import json

# def search_view(request):
#     #从json中获取数据
#     data = json.loads(request.body)
#     text = data['text']
#     page = data['page']
#
#     # #从url中获取数据
#     # text = request.GET.get('text')
#     # page = request.GET.get('page')
#
#     base_cache_key = hashlib.md5(f'search_results_{text}'.encode()).hexdigest()
#     cache_key = f'{base_cache_key}_page_{page}'
#
#     cached_results = cache.get(cache_key)
#     if cached_results is not None:
#         return JsonResponse({'code': 200, 'data': cached_results})
#
#     from .documents import ScholarDocument
#     search = ScholarDocument.search().sort('_doc')
#     results = search.filter("match", name=text).to_queryset()
#     results = list(results.values())
#     sort_and_cache_results.delay(results, base_cache_key)
#     task = sort_and_cache_results.delay(results, cache_key)
#     # task_result = AsyncResult(task.id)
#     first_page = task_result.get(timeout=10)
#
#     return JsonResponse({
#         'code': 200,
#         'data': first_page,
#     })


import time
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Search
from elasticsearch.helpers import bulk, parallel_bulk
cl = connections.create_connection()
def search_view2(request):
    start_time = time.time()
    text = request.GET.get('text')
    s = Search(using=cl, index='scholar').filter('match', name=text)
    response = s.execute()
    results = []
    for hit in response:
        results.append(hit.to_dict())
    end_time = time.time()
    return JsonResponse({
        'count': len(results),
        'results': results,
        'time': end_time - start_time
    })


