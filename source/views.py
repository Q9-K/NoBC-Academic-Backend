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
            "_source": ["display_name", "cited_by_count", "counts_by_year", "works_count", "summary_stats", "x_concepts"]
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
            "_source": ["id", "display_name", "x_concepts", "summary_stats"],
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
        es_res = elasticsearch_connection.search(index='source', body=query_body)
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


def get_authors_distribution(request):
    if request.method == 'GET':
        page_num = int(request.GET.get('page_num', 1))
        page_size = int(request.GET.get('page_size', 10))
        query_body = {}
        es_res = elasticsearch_connection.search(index='source', body=query_body)
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


def get_hot_sources(request):
    if request.method == 'GET':
        page_num = int(request.GET.get('page_num', 1))
        page_size = int(request.GET.get('page_size', 10))
        query_body = {
            "query": {
                "match_all": {}
            },
            "sort": [
                {
                    "summary_stats.2yr_mean_citedness": {
                        "order": "desc",
                        "nested": {
                            "path": "summary_stats",
                            "filter": {
                                "exists": {
                                    "field": "summary_stats.2yr_mean_citedness"
                                }
                            }
                        }
                    }
                }
            ],
            "_source": ["id", "display_name", "x_concepts", "summary_stats"],
            "from": (page_num - 1) * page_size,
            "size": page_size
        }
        es_res = elasticsearch_connection.search(index='source', body=query_body)
        res = []
        for hit in es_res['hits']['hits']:
            res.append(hit['_source'])

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


def get_authors_by_cited(request):
    if request.method == 'GET':
        source_id = request.GET.get('source_id')
        page_num = int(request.GET.get('page_num', 1))
        page_size = int(request.GET.get('page_size', 10))
        query_body = {
            "query": {
                "nested": {
                    "path": "locations",
                    "query": {
                        "nested": {
                            "path": "locations.source",
                            "query": {
                                "term": {
                                    "ilocations.source.d": {
                                        "value": source_id
                                    }
                                }
                            }
                        }
                    }
                }
            },
            """
            "aggs": {
                "all_authors": {
                    "nested": {
                        "path": "authorships"
                    },
                    "aggs": {
                        "authors_by_id": {
                            "terms": {
                                "field": "authorships.author.id.keyword",  # 使用.keyword确保对字符串进行精确匹配
                                "size": 10  # 设置返回的聚合桶的数量
                            },
                            "aggs": {
                                "total_cited_by_count": {
                                    "sum": {
                                        "field": "cited_by_count"
                                    }
                                }
                            }
                        }
                    }
                }
            },"""
            "from": (page_num - 1) * page_size,
            "size": page_size,
        }
        es_res = elasticsearch_connection.search(index='work', body=query_body)
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
                            #'operator': "and",
                        }
                    }
                }
            },
            "from": (page_num - 1) * page_size,
            "size": page_size,
        }
        query_body1 = {
            "query": {
                "nested": {
                    "path": "x_concepts",
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "x_concepts.display_name": {
                                            "query": concept,
                                            "operator": "and"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "from": (page_num - 1) * page_size,
            "size": page_size,
        }
        es_res = elasticsearch_connection.search(index='source', body=query_body)
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
