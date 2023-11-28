from django.http import JsonResponse
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections

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


# import time
# from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Search
# from elasticsearch.helpers import bulk, parallel_bulk
# cl = connections.create_connection()
# def search_view2(request):
#     start_time = time.time()
#     text = request.GET.get('text')
#     s = Search(using=cl, index='author').filter('match', name=text)
#     response = s.execute()
#     results = []
#     for hit in response:
#         results.append(hit.to_dict())
#     end_time = time.time()
#     return JsonResponse({
#         'count': len(results),
#         'results': results,
#         'time': end_time - start_time
#     })

elasticsearch_connection = connections.get_connection()


# 作者名搜索
def common_search(request):
    author_name = request.GET.get('author_name')
    search = Search(using=elasticsearch_connection, index='author').filter('match', display_name=author_name)
    search_results = search.execute()
    results = []
    for hit in search_results:
        results.append(hit.to_dict())
    return JsonResponse({
        'count': len(results),
        'results': results
    })


# 列出作者的所有作品
def get_works(request):
    # 從work index裡面找
    # 使用id還是display_name?
    author_name = request.GET.get('author_name')

    query_body = {
        "query": {
            'nested': {
                'path': 'authorships',
                'query': {
                    'nested': {
                        'path': 'authorships.author',
                        'query': {
                            'match': {
                                'authorships.author.display_name': author_name
                            }
                        }
                    }
                }
            }
        }
    }
    res = elasticsearch_connection.search(index='work', body=query_body)

    return JsonResponse({
        'result': res
    })
