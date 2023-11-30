from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from elasticsearch_dsl import connections, Search
from elasticsearch_dsl.query import Match, Term, Q, MultiMatch, Query
import threading

elasticsearch_connection = connections.get_connection()
INDEX_NAME = 'work'


def common_search(request):
    request = request.GET
    text = request.get('text')
    query_content = request.get('query_content')
    time_from = request.get('time_from')
    time_to = request.get('time_to')
    journal = request.get('journal')
    match = Q('nested', path='best_oa_location',
              query=Q('nested', path='best_oa_location__source', query=Q('match', best_oa_location__source__id='https://openalex.org/S4306400744')))
    # match = Match(best_oa_location__source__id = 'https://openalex.org/S4306400194')
    search = Search(using=elasticsearch_connection, index='work').query(match)
    search_results = search.execute()
    print(search.to_dict())
    results = []
    for hit in search_results:
        results.append(hit.to_dict())
    return JsonResponse({
        'count': len(results),
        'results': results
    })
