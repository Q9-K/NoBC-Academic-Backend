from pprint import pprint
# Create your views here.
from django.http import JsonResponse
from elasticsearch_dsl import connections, Search
from elasticsearch_dsl.query import Match, Term, Q, MultiMatch, Query, Range
from NoBC.status_code import *
from utils.view_decorator import allowed_methods

elasticsearch_connection = connections.get_connection()
INDEX_NAME = 'work'


@allowed_methods(['GET'])
def search(request):
    query_content = request.GET.get('query_content')
    time_from = request.GET.get('time_from')
    time_to = request.GET.get('time_to')
    journal = request.GET.get('journal')
    subject = request.GET.get('subject')
    institution = request.GET.get('institution')

    if not query_content:
        return JsonResponse({
            'code': PARAMS_ERROR,
            'error': True,
            'message': 'please input search text.',
            'data': {}
        })
    search = Search(using=elasticsearch_connection, index=INDEX_NAME).highlight('title', fragment_size=50)
    # if common search
    match = MultiMatch(query=query_content, fields=['abstract', 'title'])
    search = search.query(match)
    # if has time range
    if time_from and time_to:
        time_range = Range()
        search = search.query(time_range)
    # TODO
    if journal:
        pass
    # TODO
    if subject:
        pass
    # TODO
    if institution:
        pass
    search = search.source(['title', 'abstract', 'authorships', 'best_oa_location'])
    search_results = search.execute()
    results = []
    pprint(search_results['hits']['hits'])
    for hit in search_results:
        results.append(hit.to_dict())
    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'OK',
        'data': {
            'count': len(results),
            'results': results
        },
    })


@allowed_methods(['GET'])
def get_work(request):
    ip = get_client_ip(request)
    request = request.GET
    id = request.get('id')
    search = Search(using=elasticsearch_connection, index=INDEX_NAME)
    search = search.filter('term', id=id)
    result = search.execute()
    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'OK',
        'data': {
            'count': 0,
            'results': {}
        }
    })



@allowed_methods(['GET'])
def get_popular_work(request):
    search = Search(using=elasticsearch_connection)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
