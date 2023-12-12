from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from elasticsearch_dsl import connections, Search
import threading

elasticsearch_connection = connections.get_connection()


def common_search(request):
    text = request.GET.get('text')
    search = Search(using=elasticsearch_connection, index='source').filter('match', abstract=text)
    search_results = search.execute()
    results = []
    for hit in search_results:
        results.append(hit.to_dict())
    return JsonResponse({
        'count': len(results),
        'results': results
    })


def get_sources_by_initial(request):
    initial = request.GET.get('initial')
    query_body = {
        "query": {
            'prefix': {
                'display_name': initial,
            }
        }
    }
    res = elasticsearch_connection.search(index='source', body=query_body)
    return JsonResponse({
        'result': res
    })


def get_sources_by_concept(request):
    concept = request.GET.get('concept')
    query_body = {
        "query": {
            'nested': {
                'path': 'x_concepts',
                'query': {
                    'match': {
                        'x_concepts.display_name': concept,
                        'operator': "and",
                    }
                }
            }
        }
    }
    res = elasticsearch_connection.search(index='source', body=query_body)
    return JsonResponse({
        'result': res
    })


