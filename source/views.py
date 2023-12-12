from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from elasticsearch_dsl import connections, Search
from NoBC.status_code import *
import threading

elasticsearch_connection = connections.get_connection()


def get_source_by_id(request):
    if request.method == 'GET':
        source_id = request.GET.get('source_id')
        query_body = {
            "query": {
                "match": {
                    "id": source_id,
                }
            },
        }
        es_res = elasticsearch_connection.search(index='source', body=query_body)
        res = es_res['hits']['hits'][0]['_source']

        return JsonResponse({
            'code': SUCCESS,
            'error': False,
            'message': '查询成功',
            'data': res,
        })
    else:
        return JsonResponse({
            'code': METHOD_ERROR,
            'error': True,
            'message': '请求方式错误',
        })


def get_sources_by_initial(request):
    if request.method == 'GET':
        initial = request.GET.get('initial')
        page_num = int(request.GET.get('page_num', 1))
        page_size = int(request.GET.get('page_size', 10))
        query_body = {
            "query": {
                'match_phrase_prefix': {
                    'display_name': initial,
                }
            },
            "from": (page_num - 1) * page_size,
            "size": page_size,
        }
        search_query = {
            "query": {
                "match": {
                    'display_name': {
                        "query": initial,
                        "operator": "and",
                        "analyzer": "edge_ngram_search_analyzer",
                        "search_analyzer": "standard"
                    }
                }
            }
        }
        es_res = elasticsearch_connection.search(index='source', body=search_query)
        res = {
            'total': es_res['hits']['total']['value'],
            'sources': [],
        }
        for hit in es_res['hits']['hits']:
            res['sources'].append(hit['_source'])

        return JsonResponse({
            'code': SUCCESS,
            'error': False,
            'message': '查询成功',
            'data': res,
        })
    else:
        return JsonResponse({
            'code': METHOD_ERROR,
            'error': True,
            'message': '请求方式错误',
        })


def get_sources_by_concept(request):
    if request.method == 'GET':
        concept = request.GET.get('concept')
        page_num = int(request.GET.get('page_num', 1))
        page_size = int(request.GET.get('page_size', 10))
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
            },
            "from": (page_num - 1) * page_size,
            "size": page_size,
        }
        es_res = elasticsearch_connection.search(index='source', body=query_body)
        res = es_res['hits']['hits']

        return JsonResponse({
            'code': SUCCESS,
            'error': False,
            'message': '查询成功',
            'data': res,
        })
    else:
        return JsonResponse({
            'code': METHOD_ERROR,
            'error': True,
            'message': '请求方式错误',
        })
