import heapq

from celery import shared_task
from django.core.cache import cache
from django.http import JsonResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
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
    if(language):
        s = s.source(['id', 'chinese_display_name'])
    else:
        s = s.source(['id', 'display_name'])
    # 执行搜索
    response = s.execute()

    response = response.to_dict()['hits']['hits']

    results=[]
    for hit in response:
        source_data = hit['_source']
        results.append(source_data)

    # 返回搜索结果
    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})


def get_tree(request):
    subdomains = {}
    parent_id = request.GET.get('id')
    current_year = 2023
    # 第一层子领域查询
    first_level_subdomains = client.search(
        index="concept",
        body={
            "query": {"term": {"parent_id": parent_id}},
            "sort": [{f"counts_by_year.{current_year}.works_count": {"order": "desc"}}],
            "_source": ["id", "name", "counts_by_year"]
        }
    )

    for domain in first_level_subdomains['hits']['hits']:
        domain_id = domain['_source']['id']
        domain_name = domain['_source']['name']

        # 第二层子领域查询
        second_level_subdomains = client.search(
            index="concept",  # 索引名作为位置参数
            body={  # 查询体作为关键字参数
                "query": {
                    "term": {"parent_id": domain_id}
                },
                "_source": ["id", "name"]
            }
        )

        subdomains[domain_id] = {
            "name": domain_name,
            "subdomains": [sub['_source'] for sub in second_level_subdomains['hits']['hits']]
        }

    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': subdomains})


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
            "_source": ["id", "display_name","summary_stats.h_index"],
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
            "_source": ["id", "chinese_display_name","summary_stats.h_index"],
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



