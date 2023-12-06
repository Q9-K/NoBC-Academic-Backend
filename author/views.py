from django.http import JsonResponse
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from author.models import Author
from NoBC.status_code import *

elasticsearch_connection = connections.get_connection()


# 根据作者名搜索，需要分页，只取前1w条以内的数据
def get_author_by_name(request):
    if request.method == 'GET':
        author_name = request.GET.get('author_name')
        page_num = int(request.GET.get('page_num', 1))
        page_size = int(request.GET.get('page_size', 10))
        query_body = {
            "query": {
                "match": {
                    "display_name": author_name
                }
            },
            "from": (page_num - 1) * page_size,
            "size": page_size
        }
        es_res = elasticsearch_connection.search(index='author', body=query_body)
        res = {
            'total': es_res['hits']['total']['value'],
            'authors': []
        }
        for hit in es_res['hits']['hits']:
            res['authors'].append(hit['_source'])

        return JsonResponse({
            'code': SUCCESS,
            'error': False,
            'message': 'success',
            'data': res
        })
    else:
        return JsonResponse({
            'code': METHOD_ERROR,
            'error': True,
            'message': '请求方式错误'
        })


# 根据作者id获取作者信息
def get_author_by_id(request):
    author_id = request.GET.get('author_id')
    query_body = {
        "query": {
            "term": {
                "id": author_id
            }
        }
    }
    es_res = elasticsearch_connection.search(index='author', body=query_body)
    res = es_res['hits']['hits'][0]['_source']
    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'success',
        'data': res
    })


# 根据作者id列出指定作者的所有作品，同样需要分页
def get_works(request):
    author_id = request.GET.get('author_id')
    query_body = {
        "query": {
            'nested': {
                'path': 'authorships',
                'query': {
                    'nested': {
                        'path': 'authorships.author',
                        'query': {
                            'term': {
                                'authorships.author.id': author_id
                            }
                        }
                    }
                }
            }
        }
    }
    res = elasticsearch_connection.search(index='work', body=query_body)

    return JsonResponse({
        'code': 0,
        'error': False,
        'message': 'success',
        'data': res
    })


# 热门作者
def get_hot_authors(request):
    # 从mysql里面搜索，按views排序
    authors = Author.objects.order_by('-views')[:10]
    res = []
    for author in authors:
        res.append({
            'id': author.id,
            'display_name': author.display_name,
            'views': author.views
        })

    return JsonResponse({
        'code': 0,
        'msg': 'success',
        'data': res
    })


# 根据指定id获取关联作者
def get_related_authors(request):
    pass


# 根据作者id获取作者的维度信息
def get_scholar_metrics(request):
    author_id = request.GET.get('author_id')
    query_body = {
        "query": {
            "term": {
                "id": author_id
            }
        },
        "_source": ["works_count", "cited_by_count", "summary_stats"]
    }
    es_res = elasticsearch_connection.search(index='author', body=query_body)
    res = es_res['hits']['hits'][0]['_source']
    return JsonResponse({
        'code': SUCCESS,
        'msg': 'success',
        'data': res
    })


def test_merge(request):
    return JsonResponse({
        'code': Commons.SUCCESS,
        'msg': 'success',
        'data': 'test'
    })
