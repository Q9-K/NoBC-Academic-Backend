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


