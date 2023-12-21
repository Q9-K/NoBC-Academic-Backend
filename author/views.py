from django.http import JsonResponse
from author.models import Author
from utils.view_decorator import allowed_methods
from NoBC.status_code import *
from author.es import *

elasticsearch_connection = connections.get_connection()


# 1、根据作者名搜索，需要分页，只取前1w条以内的数据
# 2、对结果进行聚合，只改变排序方式时不改变聚合结果
# 3、使用聚合指标对结果（这个结果能不能暂存一下）进行过滤，过滤后再进行聚合
@allowed_methods(['GET'])
def get_author_by_name(request):
    author_name = request.GET.get('author_name')
    page_num = int(request.GET.get('page_num', 1))
    page_size = int(request.GET.get('page_size', 10))
    order_by = request.GET.get('order_by')
    institution = request.GET.get('institution')
    h_index_up = request.GET.get('h_index_up')
    h_index_down = request.GET.get('h_index_down')

    query_body = {
        "query": {
            "match": {
                "display_name": author_name
            }
        },
        "from": (page_num - 1) * page_size,
        "size": page_size
    }
    if institution != '':
        query_body['query']['bool'] = {
            "must": {
                "match": {
                    "last_known_institution.display_name": institution
                }
            }
        }
    if h_index_up != '' and h_index_down != '':
        # 不需要筛选institution
        if query_body['query'].get('bool') is None:
            query_body['query']['bool'] = {
                "must": {
                    "range": {
                        "summary_stats.h_index": {
                            "gte": h_index_down,
                            "lte": h_index_up
                        }
                    }
                }
            }
        else:
            query_body['query']['bool']['must']['range'] = {
                "summary_stats.h_index": {
                    "gte": h_index_down,
                    "lte": h_index_up
                }
            }

    es_query_res = elasticsearch_connection.search(index='author', body=query_body)
    res = {
        'total': es_query_res['hits']['total']['value'],
        'authors': []
    }
    for hit in es_query_res['hits']['hits']:
        res['authors'].append(hit['_source'])

    # 点击搜索按钮/按照聚合指标过滤时，order_by为空，这时候需要对结果进行按照 institution 和 h-index 范围进行聚合
    if order_by == '':
        # h-index 聚合
        range_list = [{
            "to": 10
        }]
        for i in range(10, 50, 10):
            range_list.append({
                "from": i,
                "to": i + 10
            })
        range_list.append({
            "from": 50
        })
        agg_body = {
            "query": {
                "match": {
                    "display_name": author_name
                }
            },
            "aggs": {
                "agg_term_institution": {
                    "terms": {
                        "field": "last_known_institution.display_name.keyword",
                    }
                }
            }
        }
        es_agg_res = elasticsearch_connection.search(index="author", body=agg_body)
        # res['institutions'] = []
        # for bucket in es_agg_res['aggregations']['agg_term_institution']['buckets']:
        #     tmp_institution = {
        #         'institution': bucket['key'],
        #         'count': bucket['doc_count']
        #     }
        #     res['institutions'].append(tmp_institution)
        #
        # res['h_index'] = []
        # for bucket in es_agg_res['aggregations']['agg_range_h_index']['buckets']:
        #     tmp_h_index = {
        #         'h_index': bucket['key'],
        #         'count': bucket['doc_count']
        #     }
        #     res['h_index'].append(tmp_h_index)

    # 点击排序/分页按钮时，order_by不为空，不需要对结果进行聚合
    else:
        pass

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'success',
        'data': res,
        'es_res': es_agg_res
    })


# 根据作者id获取作者信息
@allowed_methods(['GET'])
def get_author_by_id(request):
    author_id = request.GET.get('author_id')

    es_res = es_get_author_by_id(author_id)

    if es_res['hits']['total']['value'] != 0:
        source = es_res['hits']['hits'][0]['_source']
        res = {
            'avatar': source['avatar'],
            'name': source['display_name'],
            'chineseName': source['chinese_name'],
            'title': source['title'],
            'phone': source['phone'],
            'fax': source['fax'],
            'email': source['email'],
            'englishAffiliation': source['last_known_institution']['display_name'],
            'chineseAffiliation': source['last_known_institution']['chinese_name'],
            'address': source['address'],
            'personalWebsite': source['personal_website'],
            'officialWebsite': source['official_website'],
            'google': source['google'],
            'twitter': source['twitter'],
            'facebook': source['facebook'],
            'youtube': source['youtube'],
            'gender': source['gender'],
            'language': source['language']
        }
    else:
        res = {}

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'success',
        'data': res
    })


# 根据作者id列出指定作者的所有作品，需要分页
@allowed_methods(['GET'])
def get_works(request):
    author_id = request.GET.get('author_id')
    page_num = int(request.GET.get('page_num', 1))
    page_size = int(request.GET.get('page_size', 10))
    res = es_get_works(author_id, page_num, page_size)

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'success',
        'data': res
    })


# 查找指定领域的权威作者
@allowed_methods(['GET'])
def get_hot_authors(request):

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
@allowed_methods(['GET'])
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
                tmp_dic['avatar'] = tmp_author_source['avatar']
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
@allowed_methods(['GET'])
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

    source = es_res['hits']['hits'][0]['_source']
    res = {
        'Papers': source['works_count'],
        'Citation': source['cited_by_count'],
        'H-Index': source['summary_stats']['h_index']
    }

    return JsonResponse({
        'code': SUCCESS,
        'msg': 'success',
        'data': res
    })


# 上传学者简介信息
@allowed_methods(['POST'])
def post_scholar_intro_information(request):
    author_id = request.POST.get('authorId')
    work_experience = request.POST.get('workExperience')
    personal_summary = request.POST.get('personalSummary')
    education_background = request.POST.get('educationBackground')

    # 写入es
    update_body = {
        "query": {
            "term": {
                "id": author_id,
            }
        },
        "script": {
            "source": "ctx._source.work_experience = params.work_experience; "
                      "ctx._source.personal_summary = params.personal_summary; "
                      "ctx._source.education_background = params.education_background",
            "params": {
                "work_experience": work_experience,
                "personal_summary": personal_summary,
                "education_background": education_background
            }
        }
    }
    # 局部更新
    elasticsearch_connection.update_by_query(index='author', body=update_body)

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'msg': 'success',
        'data': {}
    })


# 上传学者基本信息
@allowed_methods(['POST'])
def post_scholar_basic_information(request):
    author_id = request.POST.get('authorId')

    # 写入es
    update_body = {}

    # 局部更新
    elasticsearch_connection.update_by_query(index='author', body=update_body)

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'msg': 'success',
        'data': {}
    })
