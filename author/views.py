from django.http import JsonResponse
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from author.models import Author
from utils.view_decorator import allowed_methods
from NoBC.status_code import *
from author.es import *

elasticsearch_connection = connections.get_connection()


# 根据作者名搜索，需要分页，只取前1w条以内的数据
def get_author_by_name(request):
    author_name = request.GET.get('author_name')
    page_num = int(request.GET.get('page_num', 1))
    page_size = int(request.GET.get('page_size', 10))
    query_body = {
        "query": {
            "match": {
                "display_name": author_name
            }
        },
        "from": page_num,
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


# 根据作者id获取作者信息
def get_author_by_id(request):
    author_id = request.GET.get('author_id')

    es_res = es_get_author_by_id(author_id)

    if es_res['hits']['total']['value'] != 0:
        res = es_res['hits']['hits'][0]['_source']
    else:
        res = {}

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'success',
        'data': res
    })


# 根据作者id列出指定作者的所有作品，需要分页吗？？
def get_works(request):
    author_id = request.GET.get('author_id')
    res = es_get_works(author_id)

    return JsonResponse({
        'code': SUCCESS,
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
        'code': SUCCESS,
        'msg': 'success',
        'data': res
    })


# 根据指定id获取关联作者（10个以内）
def get_co_author_list(request):
    author_id = request.GET.get('author_id')
    works = es_get_works(author_id)

    res_id = []
    res = []
    for work in works['hits']['hits']:
        if len(res) >= 10:
            break
        author_ships = work['_source']['authorships']
        for author_ship in author_ships:
            if author_ship['author']['id'] != author_id and author_ship['author']['id'] not in res_id:
                res_id.append(author_ship['author']['id'])
                tmp_dic = {'name': author_ship['author']['display_name']}
                if len(author_ship['institutions']) > 0:
                    tmp_dic['organization'] = author_ship['institutions'][0]['display_name']
                else:
                    tmp_dic['organization'] = ''

                tmp_author = es_get_author_by_id(author_ship['author']['id'])
                tmp_author_source = tmp_author['hits']['hits'][0]['_source']
                tmp_dic['avatar'] = ''
                tmp_dic['paperCount'] = tmp_author_source['works_count']
                tmp_dic['ScholarId'] = author_ship['author']['id']
                res.append(tmp_dic)

            if len(res) >= 10:
                break

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'msg': 'success',
        'data': res,
    })


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


# 上传学者简介信息（或者说有个维护学者信息的接口，不只是简介，更多的社交媒体账号之类的）
@allowed_methods(['POST'])
def post_scholar_basic_information(request):
    work_experience = request.POST.get('workExperience')
    personal_summary = request.POST.get('personalSummary')
    education_background = request.POST.get('educationBackground')

    # 写入es

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'msg': 'success',
        'data': {}
    })

# 高级检索
# def
