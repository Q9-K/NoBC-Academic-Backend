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
                'prefix': {
                    'display_name.keyword': initial,
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
        query_body = {
            "query": {
                "nested": {
                    "path": "locations",
                    "query": {
                        "nested": {
                            "path": "locations.source",
                            "query": {
                                "term": {
                                    "locations.source.id": {
                                        "value": source_id
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "size": 10000,
        }
        es_res = elasticsearch_connection.search(index='work', body=query_body)
        res1 = {
            'total': es_res['hits']['total']['value'],
            'sources': [],
        }
        for hit in es_res['hits']['hits']:
            res1['sources'].append(hit['_source'])

        print(len(res1.get('sources')))

        res = dict()
        for work in res1['sources']:
            cited_by_count = work['cited_by_count']
            authorships = work['authorships']
            for author in authorships:
                author_id = author['author']['id']
                if author_id in res:
                    res[author_id]['cited_by_count'] += cited_by_count
                    res[author_id]['work_count'] += 1
                else:
                    new_author = {
                        'author': author['author'],
                        'cited_by_count': cited_by_count,
                        'work_count': 1,
                    }
                    res[author_id] = new_author
        print(len(res))
        sorted_res = [value for key, value in sorted(res.items(), key=lambda x: x[1]["cited_by_count"], reverse=True)]

        query_body1 = {
            "query": {
                "nested": {
                    "path": "locations",
                    "query": {
                        "nested": {
                            "path": "locations.source",
                            "query": {
                                "term": {
                                    "locations.source.id": {
                                        "value": source_id
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "aggs": {
                "all_authors": {
                    "nested": {
                        "path": "authorships.author"
                    },
                    "aggs": {
                        "authors_by_id": {
                            "terms": {
                                "field": "authorships.author.id.keyword",
                                "size": 10
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
            }
        }

        return JsonResponse({
            'code': SUCCESS,
            'error': False,
            'message': '查询成功',
            'data': sorted_res,
        })
    else:
        return JsonResponse({
            'code': METHOD_ERROR,
            'error': True,
            'message': '请求方式错误',
        })


def search_sources(request):
    if request.method == 'GET':
        keyword = request.GET.get('journal_name')
        page_num = int(request.GET.get('page_num', 1))
        page_size = int(request.GET.get('page_size', 10))
        query_body = {
            "query": {
                "match": {
                    "display_name": {
                        "query": keyword,
                        "fuzziness": "auto"
                    }
                }
            },
            "_source": ["id", "display_name", "x_concepts", "summary_stats"],
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
                            # 'operator': "and",
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
