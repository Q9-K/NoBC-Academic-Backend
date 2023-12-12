import heapq

from celery import shared_task
from django.core.cache import cache
from django.http import JsonResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
from NoBC.status_code import *
from utils.view_decorator import allowed_methods

# Create your views here.

client = connections.get_connection()


@allowed_methods(['GET'])
def get_level_0(request):
    language = request.GET.get('language', 0)
    # 创建搜索对象
    try:
        s = Search(using=client, index="concept")
    except Exception as e:
        return JsonResponse({'code': 10005, 'msg': '创建搜索对象失败'})
    # 添加过滤条件
    s = s.filter("term", level=0)
    if (language):
        s = s.source(['id', 'chinese_display_name'])
    else:
        s = s.source(['id', 'display_name'])
    # 执行搜索
    response = s.execute()

    response = response.to_dict()['hits']['hits']

    results = []
    for hit in response:
        source_data = hit['_source']
        results.append(source_data)

    # 返回搜索结果
    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})


def get_subdomains(request):
    language = request.GET.get('language', 0)
    id = request.GET.get('id')
    # 构建查询
    if language:
        query = {
            "query": {
                "nested": {
                    "path": "ancestors",
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"ancestors.id": id}},

                            ]
                        }
                    }
                }
            },
            "sort": [
                {
                    "summary_stats.h_index": {
                        "order": "desc",
                        "nested": {
                            "path": "summary_stats"
                        }
                    }
                }
            ],
            "_source": ["id", "chinese_display_name"]
        }
    else:
        query = {
            "query": {
                "nested": {
                    "path": "ancestors",
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"ancestors.id": id}},

                            ]
                        }
                    }
                }
            },
            "sort": [
                {
                    "summary_stats.h_index": {
                        "order": "desc",
                        "nested": {
                            "path": "summary_stats"
                        }
                    }
                }
            ],
            "_source": ["id", "display_name"]
        }
    response = client.search(index="concept", body=query)

    # 提取结果
    results = []
    for hit in response['hits']['hits']:
        source_data = hit['_source']
        results.append(source_data)
    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})


def search_concept_by_keyword(request):
    keyword = request.GET.get('keyword')
    print(keyword)
    language = request.GET.get('language', 0)
    query = {}
    if language == '0':
        query = {
            "query": {
                "match": {
                    "display_name": {
                        "query": keyword,
                        "fuzziness": "AUTO"
                    }
                }
            },
            "_source": ["id", "display_name", "summary_stats.h_index"],
            "sort": [
                {
                    "summary_stats.h_index": {
                        "order": "desc",
                        "nested": {
                            "path": "summary_stats"
                        }
                    }
                }
            ],
            "size": 100
        }
    else:
        query = {
            "query": {
                "match": {
                    "chinese_display_name": {
                        "query": keyword,
                        "fuzziness": "AUTO"
                    }
                }
            },
            "_source": ["id", "chinese_display_name", "summary_stats.h_index"],
            "sort": [
                {
                    "summary_stats.h_index": {
                        "order": "desc",
                        "nested": {
                            "path": "summary_stats"
                        }
                    }
                }
            ],
            "size": 100
        }

    results = []
    response = client.search(index="concept", body=query)
    for hit in response['hits']['hits']:
        source_data = hit['_source']
        results.append(source_data)

    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})


def get_concept_by_id(request):
    id = request.GET.get('id')
    language = request.GET.get('language', 0)
    query = {}
    if language == '0':
        query = {
            "query": {
                "term": {
                    "id": id
                }
            },
            "_source": ["id", "display_name", "level", "description", "summary_stats", "works_count", "cited_by_count",
                        "related_concepts", "ancestors", "image_url", "counts_by_year"],
            "size": 1
        }
    else:
        query = {
            "query": {
                "term": {
                    "id": id
                }
            },
            "_source": ["id", "chinese_display_name", "level", "chinese_description", "summary_stats", "works_count",
                        "cited_by_count", "related_concepts", "ancestors", "image_url", "counts_by_year"],
            "size": 1
        }

    results = []
    response = client.search(index="concept", body=query)
    for hit in response['hits']['hits']:
        source_data = hit['_source']
        results.append(source_data)

    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})
