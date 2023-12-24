import heapq
import random

from celery import shared_task
from django.core.cache import cache
from django.http import JsonResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections

from concept.models import Concept
from user.models import User, History
from NoBC.status_code import *
from utils.generate_image import generate_image
from utils.view_decorator import allowed_methods, login_required
from utils.translate import translate
from utils.qos import upload_file, get_file

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

    s = s.source(['id', 'display_name', 'chinese_display_name', 'level'])

    s = s[0:100]  # 获取前100个结果
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

    # 提取结果并检查是否需要翻译
    to_translate = []
    translate_mapping = []
    results = []

    for hit in response['hits']['hits']:
        source_data = hit['_source']
        document_id = hit['_id']  # 捕获文档ID

        if 'chinese_display_name' not in source_data or source_data['chinese_display_name'] == '':
            to_translate.append(source_data['display_name'])
            translate_mapping.append((document_id, source_data))
        results.append(source_data)
        # 进行翻译
    if to_translate:
        translated = translate("\n".join(to_translate))

        # 将翻译结果更新回对应的字段并写回 Elasticsearch
        for (document_id, source_data), translated_name in zip(translate_mapping, translated):
            source_data['chinese_display_name'] = translated_name

            # 更新 Elasticsearch 文档
            update_body = {"doc": source_data}
            client.update(index="concept", id=document_id, body=update_body)

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
        translated = translate("\n".join(to_translate))  # 假设 translate 函数可以处理这个字符串

        # 更新 Elasticsearch 并更新返回数据
        for i, document_id in enumerate(ids_to_update):
            translated_name = translated[i] if i < len(translated) else None
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
    if cache.get(id):
        print('cache hit')
        return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': cache.get(id)})
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

    response = client.search(index="concept", body=query)
    results = []
    for hit in response['hits']['hits']:
        source_data = hit['_source']
        document_id = hit['_id']

        # 收集需要翻译的 display_name
        to_translate = []
        translate_mapping = []  # 存储需要翻译的对象引用和字段名称

        if not source_data['image_url']:
            if source_data['chinese_display_name'] == '':
                source_data['image_url'] = generate_image(source_data['display_name'])
            else:
                source_data['image_url'] = generate_image(source_data['chinese_display_name'])

        # 翻译 ancestors 和 related_concepts 中的 chinese_display_name

        # 检查最外层的 chinese_display_name 是否需要翻译
        if 'chinese_display_name' not in source_data or source_data['chinese_display_name'] == '':
            to_translate.append(source_data['display_name'])
            translate_mapping.append((source_data, 'chinese_display_name'))
        if 'chinese_description' not in source_data or source_data['chinese_description'] == '':
            to_translate.append(source_data['description'])
            translate_mapping.append((source_data, 'chinese_description'))

        for field in ['ancestors', 'related_concepts']:
            if field in source_data:
                for item in source_data[field]:
                    if 'chinese_display_name' not in item or item['chinese_display_name'] == '':
                        to_translate.append(item['display_name'])
                        translate_mapping.append((item, 'chinese_display_name'))

        # 进行翻译
        if to_translate:
            translated = translate("\n".join(to_translate))

            # 将翻译结果更新回对应的字段
            for part, (obj, field) in zip(translated, translate_mapping):
                obj[field] = part

            # 更新 Elasticsearch 文档
            update_body = {"doc": source_data}
            client.update(index="concept", id=document_id, body=update_body)

        results.append(source_data)
    cache.set(id, results, timeout=60 * 60 * 30)
    return JsonResponse({'code': SUCCESS, 'msg': 'no error', 'data': results})


@allowed_methods(['GET'])
def get_ancestor_concepts(request):
    id = request.GET.get('id')
    query = {
        "query": {
            "term": {
                "id": id
            }
        },
        "_source": ["id", "ancestors"],
        "size": 1
    }

    response = client.search(index="concept", body=query)
    results = []
    for hit in response['hits']['hits']:
        source_data = hit['_source']
        document_id = hit['_id']

        # 收集需要翻译的 display_name
        to_translate = []
        translate_mapping = []  # 存储需要翻译的对象引用和字段名称

        for field in ['ancestors']:
            if field in source_data:
                for item in source_data[field]:
                    if 'chinese_display_name' not in item or item['chinese_display_name'] == '':
                        to_translate.append(item['display_name'])
                        translate_mapping.append((item, 'chinese_display_name'))

        # 进行翻译
        if to_translate:
            translated = translate("\n".join(to_translate))

            # 将翻译结果更新回对应的字段
            for part, (obj, field) in zip(translated, translate_mapping):
                obj[field] = part

            # 更新 Elasticsearch 文档
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
    to_translate = []
    ids_to_update = []  # 仅存储需要更新的文档的 document_id
    for hit in response['hits']['hits']:
        source_data = hit['_source']

        if source_data['chinese_display_name'] == '':
            to_translate.append(source_data['display_name'])
            ids_to_update.append(hit['_id'])  # 仅存储缺少字段的文档的 document_id

        results.append(source_data)

    # 进行翻译
    if to_translate:
        translated = translate("\n".join(to_translate))

        # 分配翻译结果并更新 Elasticsearch
        for i, document_id in enumerate(ids_to_update):
            if i < len(translated):
                update_body = {"doc": {"chinese_display_name": translated[i]}}
                client.update(index="concept", id=document_id, body=update_body)

                # 同时更新返回的结果集
                for result in results:
                    if result['id'] == document_id:
                        result['chinese_display_name'] = translated[i]

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


@allowed_methods(['GET'])
@login_required
def get_works_with_followed_concepts(request):
    user = request.user
    user: User
    concept_focus = user.concept_focus.all()
    results = []
    query = {}

    if len(concept_focus) > 0:
        # 收集每个概念的论文
        for concept in concept_focus:
            concept: Concept
            id = concept.id.split('/')[-1]

            # 构建查询
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
                },
                "_source": ["abstract", "title", "visit_count", "cited_by_count",
                         "publication_date", "language", "authorships",
                         "locations", "id", "type", "citation"],
                "sort": [
                    {
                        "cited_by_count": {
                            "order": "desc"
                        }
                    }
                ],
                "size": 50  # 每个概念获取 100 篇论文
            }
    else:
        recent_histories = History.objects.filter(user=user).order_by('-date_time')[:8]
        if len(recent_histories) > 0:
            # 获取论文 ID
            work_ids = [history.work.id for history in recent_histories]

            # 获取相关论文的 concepts ID
            concept_ids = set()
            for work_id in work_ids:
                query = {
                    "query": {
                        "match": {
                            "id": work_id
                        }
                    },
                    "_source": ["concepts.id"]
                }
                response = client.search(index="work", body=query)
                for hit in response['hits']['hits']:
                    concepts = hit["_source"].get("concepts", [])
                    for concept in concepts:
                        concept_ids.add(concept["id"])

            # 对每个 concept ID 进行搜索
            for concept_id in concept_ids:
                query = {
                    "query": {
                        "nested": {
                            "path": "concepts",
                            "query": {
                                "bool": {
                                    "must": [
                                        {"match": {"concepts.id": concept_id}}
                                    ]
                                }
                            }
                        }
                    },
                    "_source": ["abstract", "title", "visit_count", "cited_by_count",
                                "publication_date", "language", "authorships",
                                "locations", "id", "type", "citation"],
                    "sort": [{"cited_by_count": {"order": "desc"}}],
                    "size": 50  # 获取 100 篇论文
                }
        else:
            # 获取最热门的 100 篇论文
            query = {
                "query": {
                    "match_all": {}
                },
                "_source": ["abstract", "title", "visit_count", "cited_by_count",
                            "publication_date", "language", "authorships",
                            "locations", "id", "type", "citation"],
                "sort": [{"cited_by_count": {"order": "desc"}}],
                "size": 100  # 获取 100 篇论文
            }

    # 执行搜索
    response = client.search(index="work", body=query)
    # 将结果添加到 results 列表
    for hit in response['hits']['hits']:
        source = hit["_source"]
        # 构造 highlight 和 other 数据结构
        result_item = {
            "highlight": {
                    "abstract": [source.get("abstract", "")],
                    "title": [source.get("title", "")]
                },
                "other": source
            }
        results.append(result_item)
    results = random.sample(results, 10)
    return JsonResponse(results, safe=False)
