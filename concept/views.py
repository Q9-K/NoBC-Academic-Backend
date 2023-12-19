import heapq

from celery import shared_task
from django.core.cache import cache
from django.http import JsonResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
from NoBC.status_code import *
from utils.generate_image import generate_image
from utils.view_decorator import allowed_methods
from utils.translate import translate

# Create your views here.

client = connections.get_connection()


@allowed_methods(['GET'])
def get_level_0(request):
    # 创建搜索对象
    try:
        s = Search(using=client, index="concept")
    except Exception as e:
        return JsonResponse({'code': 10005, 'msg': '创建搜索对象失败'})
    # 添加过滤条件
    s = s.filter("term", level=0)

    s = s.source(['id', 'display_name','chinese_display_name'])
    # 执行搜索
    response = s.execute()

    response = response.to_dict()['hits']['hits']

    results = []
    for hit in response:
        source_data = hit['_source']
        results.append(source_data)

    # 返回搜索结果
    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})

@allowed_methods(['GET'])
def get_subdomains(request):
    id = request.GET.get('id')
    # 构建查询

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
                    "order": "desc"
                }
            }
        ],
        "_source": ["id", "display_name", "chinese_display_name"]
    }

    response = client.search(index="concept", body=query)

    # 提取结果
    results = []
    for hit in response['hits']['hits']:
        source_data = hit['_source']
        results.append(source_data)
    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})

@allowed_methods(['GET'])
def search_concept_by_keyword(request):
    language = request.GET.get('language')
    keyword = request.GET.get('keyword')
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
            "_source": ["id", "display_name", "chinese_display_name", "summary_stats.h_index"],
            "sort": [
                {
                    "summary_stats.h_index": {
                        "order": "desc"
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
            "_source": ["id", "display_name", "chinese_display_name", "summary_stats.h_index"],
            "sort": [
                {
                    "summary_stats.h_index": {
                        "order": "desc"
                    }
                }
            ],
            "size": 100
        }

    results = []
    to_translate = []
    ids_to_update = []  # 用于存储需要更新的文档的ID
    response = client.search(index="concept", body=query)

    # 收集需要翻译的数据
    for hit in response['hits']['hits']:
        source_data = hit['_source']
        results.append(source_data)

        if not source_data.get('chinese_display_name'):
            to_translate.append(source_data['display_name'])
            ids_to_update.append(hit['_id'])

    # 进行翻译
    if len(to_translate) > 0:
        translated = translate("||".join(to_translate))  # 假设 translate 函数可以处理这个字符串
        translated_names = translated.split("||")

        # 更新 Elasticsearch 并更新返回数据
        for i, document_id in enumerate(ids_to_update):
            translated_name = translated_names[i] if i < len(translated_names) else None
            if translated_name:
                update_body = {"doc": {"chinese_display_name": translated_name}}
                client.update(index="concept", id=document_id, body=update_body)
                # 同时更新返回的结果集
                for result in results:
                    if result['id'] == document_id:  # 假设 'id' 是文档的唯一标识符
                        result['chinese_display_name'] = translated_name

    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})

@allowed_methods(['GET'])
def get_concept_by_id(request):
    id = request.GET.get('id')
    query = {
        "query": {
            "term": {
                "id": id
            }
        },
        "_source": ["id", "display_name", "chinese_display_name", "level", "description", "chinese_description",
                    "summary_stats", "works_count", "cited_by_count",
                    "related_concepts", "ancestors", "image_url", "counts_by_year"],
        "size": 1
    }

    results = []
    response = client.search(index="concept", body=query)
    for hit in response['hits']['hits']:
        source_data = hit['_source']
        document_id = hit['_id']  # Capture the document ID
        if source_data['chinese_display_name'] == '':
            all = translate(source_data['display_name']+"||"+source_data['description'])
            #根据空格分割
            all = all.split("||")
            source_data['chinese_display_name'] = all[0]
            source_data['chinese_description'] = all[1]

        if source_data['chinese_description'] == '':
            all = translate(source_data['description'])
            source_data['chinese_description'] = all
        if source_data['image_url'] == '':
            if source_data['chinese_display_name'] == '':
                source_data['image_url'] = generate_image(source_data['display_name'])
            else:
                source_data['image_url'] = generate_image(source_data['chinese_display_name'])

        update_body = {"doc": source_data}
        client.update(index="concept", id=document_id, body=update_body)



        results.append(source_data)

    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})

@allowed_methods(['GET'])
def get_hot_concepts(request):
    query = {
        "size": 30,
        "query": {
            "match_all": {}
        },
        "sort": {
            "_script": {
                "type": "number",
                "script": {
                    "lang": "painless",
                    "source": "doc['summary_stats.h_index'].value * (4 - Math.abs(3 - doc['level'].value))"
                },
                "order": "desc"
            }
        },
        "_source": ["id", "display_name", "chinese_display_name", "level", "summary_stats.h_index"]
    }
    response = client.search(index='concept', body=query)

    results = []
    for hit in response['hits']['hits']:
        source_data = hit['_source']
        results.append(source_data)

    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})
@allowed_methods(['GET'])
def search_works_by_concept(request):
    id = request.GET.get('id')

    query = {
        "query": {
            "nested": {
                "path": "concepts",
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"concepts.id": id}}
                        ]
                    }
                }
            }
        }
    }

    # 执行搜索
    response = client.search(index="work", body=query)

    # 处理结果
    results = [hit["_source"] for hit in response['hits']['hits']]
    return JsonResponse(results, safe=False)


def search_works_with_empty_concept_id(request):
    # Elasticsearch 查询，查找 concepts.id 字段为空的文档
    query = {
        "query": {
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "concepts.id"
                    }
                }
            }
        }
    }

    # 执行搜索
    response = client.search(index="work", body=query)
    # 处理结果
    results = [hit["_source"] for hit in response['hits']['hits']]
    return JsonResponse(results, safe=False)