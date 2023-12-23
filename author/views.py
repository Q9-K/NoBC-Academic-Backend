import json

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
            "bool": {
                "must": [
                    {
                        "match": {
                            "display_name": author_name
                        },
                    }
                ]
            }
        },
        "from": (page_num - 1) * page_size,
        "size": page_size,
    }

    # 添加聚合指标过滤
    if institution != '':
        query_body['query']['bool']['must'].append({
            "term": {
                "last_known_institution.display_name": institution
            }
        })
    if h_index_up != '' and h_index_down != '':
        query_body['query']['bool']['must'].append({
            "range": {
                "summary_stats.h_index": {
                    "gte": h_index_down,
                    "lte": h_index_up
                }
            }
        })

    res = {}
    # 点击搜索按钮/按照聚合指标过滤时，order_by为空，这时候需要对结果进行按照 institution 和 h-index 范围进行聚合
    if order_by == '':
        # h-index 聚合用到的 range_list
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
            "query": query_body['query'],
            "aggs": {
                "agg_term_institution": {
                    "terms": {
                        "field": "last_known_institution.display_name",
                    }
                },
                "agg_range_h_index": {
                    "range": {
                        "field": "summary_stats.h_index",
                        "ranges": range_list
                    }
                }
            }
        }
        es_agg_res = elasticsearch_connection.search(index=AUTHOR, body=agg_body)
        res['institutions'] = []
        for bucket in es_agg_res['aggregations']['agg_term_institution']['buckets']:
            tmp_institution = {
                'institution': bucket['key'],
                'count': bucket['doc_count']
            }
            res['institutions'].append(tmp_institution)

        res['h_index'] = []
        for bucket in es_agg_res['aggregations']['agg_range_h_index']['buckets']:
            tmp_h_index = {
                'h_index': bucket['key'],
                'count': bucket['doc_count']
            }
            res['h_index'].append(tmp_h_index)
    # 点击排序/分页按钮时，order_by不为空，增加排序字段，但不需要对结果进行聚合
    # default / h - index / cite / work
    else:
        if order_by == 'h-index':
            query_body['sort'] = {
                "summary_stats.h_index": {
                    "order": "desc"
                }
            }
        elif order_by == 'cite':
            query_body['sort'] = {
                "cited_by_count": {
                    "order": "desc"
                }
            }
        elif order_by == 'work':
            query_body['sort'] = {
                "works_count": {
                    "order": "desc"
                }
            }
        else:
            pass
    # print(query_body)
    es_query_res = elasticsearch_connection.search(index=AUTHOR, body=query_body)
    res['total'] = es_query_res['hits']['total']['value']
    res['authors'] = []
    for hit in es_query_res['hits']['hits']:
        res['authors'].append(hit['_source'])

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'success',
        'data': res
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
            # 暂时不需要 chineseAffiliation
            'chineseAffiliation': None,
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


# 获取作者近几年数据
@allowed_methods(['GET'])
def get_counts_by_year(request):
    author_id = request.GET.get('author_id')
    es_res = es_get_author_by_id(author_id)

    res = []
    source = es_res['hits']['hits'][0]['_source']
    for year in source['counts_by_year']:
        res.append({
            'type': year['year'],
            'papers': year['works_count']
        })

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'success',
        'data': res
    })


# 根据作者id列出指定作者的所有作品(1w以内)，需要分页
@allowed_methods(['GET'])
def get_works(request):
    author_id = request.GET.get('author_id')
    page_num = int(request.GET.get('page_num', 1))
    page_size = int(request.GET.get('page_size', 10))
    es_res = es_get_works(author_id, page_num, page_size)

    res = {
        'total': es_res['hits']['total']['value'],
        'works': []
    }
    for hit in es_res['hits']['hits']:
        res['works'].append(hit['_source'])

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'success',
        'data': res
    })


# 查找指定领域的权威作者(h-index最高的前20个作者，不分页)
@allowed_methods(['GET'])
def get_hot_authors(request):
    concept_id = request.GET.get('concept_id')
    # 方法一
    # query_body = {
    #     "query": {
    #         "term": {
    #             "id": concept_id
    #         }
    #     }
    # }
    # es_res = elasticsearch_connection.search(index='concept', body=query_body)
    #
    # res = es_res['hits']['hits'][0]['_source']['hot_authors']

    # 方法二，实时算，看看速度
    query_body = {
        "query": {
            "nested": {
                "path": "x_concepts",
                "query": {
                    "term": {
                        "x_concepts.id": concept_id
                    }
                }
            }
        },
        "sort": {
            "summary_stats.h_index": {
                "order": "desc"
            }
        },
        "size": 20
    }
    es_res = elasticsearch_connection.search(index=AUTHOR, body=query_body)

    res = []
    for hit in es_res['hits']['hits']:
        res.append(hit['_source'])

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'msg': 'success',
        'data': res
    })


# 根据指定id获取关联作者（10个）
# （涉及全量数据，但是只需要找出来有关联的作者即可，不需要基于全量数据进行排序，所以只处理一部分就能得到结果，所以选择实时计算）
@allowed_methods(['GET'])
def get_co_author_list(request):
    author_id = request.GET.get('author_id')
    # 获取作者的所有作品(20个)，用来获取10个关联作者足够了
    works = es_get_works(author_id)
    print("works: ", len(works['hits']['hits']))

    # 已经找到的关联作者id
    res_id = []
    # 关联作者的具体信息
    res = []

    for work in works['hits']['hits']:
        if len(res) >= 10:
            break

        # 遍历作者列表
        author_ships = work['_source']['authorships']
        for author_ship in author_ships:
            # 如果作者id不是当前作者id，且作者id不在已经找到的关联作者id列表中
            if author_ship['author']['id'] != author_id and author_ship['author']['id'] not in res_id:
                res_id.append(author_ship['author']['id'])
                tmp_dic = {'name': author_ship['author']['display_name']}
                if len(author_ship['institutions']) > 0:
                    tmp_dic['organization'] = author_ship['institutions'][0]['display_name']
                else:
                    tmp_dic['organization'] = None

                tmp_author = es_get_author_by_id(author_ship['author']['id'])
                # 这里应该是都能搜得到的，除非数据导入不完整
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
        'works': works
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
    es_res = elasticsearch_connection.search(index=AUTHOR, body=query_body)

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


# 获取学者的简介信息
@allowed_methods(['GET'])
def get_scholar_intro_information(request):
    author_id = request.GET.get('author_id')
    query_body = {
        "query": {
            "term": {
                "id": author_id
            }
        }
    }
    es_res = elasticsearch_connection.search(index=AUTHOR, body=query_body)

    source = es_res['hits']['hits'][0]['_source']
    res = {
        'workExperience': source['work_experience'],
        'personalSummary': source['personal_summary'],
        'educationBackground': source['education_background']
    }

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'msg': 'success',
        'data': res
    })


# 上传学者简介信息
@allowed_methods(['POST'])
def post_scholar_intro_information(request):
    author_id = request.POST.get('author_id')
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
    elasticsearch_connection.update_by_query(index=AUTHOR, body=update_body)

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'msg': 'success',
        'data': {}
    })


# 上传学者基本信息（涉及到头像文件处理
@allowed_methods(['POST'])
def post_scholar_basic_information(request):
    author_id = request.POST.get('author_id')

    avatar = request.FILES.get('avatar')

    display_name = request.POST.get('name')
    chinese_name = request.POST.get('chineseName')
    title = request.POST.get('title')
    phone = request.POST.get('phone')
    fax = request.POST.get('fax')
    email = request.POST.get('email')
    english_affiliation = request.POST.get('englishAffiliation')
    address = request.POST.get('address')
    personal_website = request.POST.get('personalWebsite')
    official_website = request.POST.get('officialWebsite')
    google = request.POST.get('google')
    twitter = request.POST.get('twitter')
    facebook = request.POST.get('facebook')
    youtube = request.POST.get('youtube')
    gender = request.POST.get('gender')
    language = request.POST.get('language')

    # 写入es
    update_body = {
        "query": {
            "term": {
                "id": author_id,
            }
        },
        "script": {
            "source": "ctx._source.avatar = params.avatar; "
                      "ctx._source.display_name = params.display_name; "
                      "ctx._source.chinese_name = params.chinese_name; "
                      "ctx._source.title = params.title; "
                      "ctx._source.phone = params.phone; "
                      "ctx._source.fax = params.fax; "
                      "ctx._source.email = params.email; "
                      "ctx._source.last_known_institution.display_name = params.english_affiliation; "
                      "ctx._source.address = params.address; "
                      "ctx._source.personal_website = params.personal_website; "
                      "ctx._source.official_website = params.official_website; "
                      "ctx._source.google = params.google; "
                      "ctx._source.twitter = params.twitter; "
                      "ctx._source.facebook = params.facebook; "
                      "ctx._source.youtube = params.youtube; "
                      "ctx._source.gender = params.gender; "
                      "ctx._source.language = params.language",
            "params": {
                "avatar": avatar,
                "display_name": display_name,
                "chinese_name": chinese_name,
                "title": title,
                "phone": phone,
                "fax": fax,
                "email": email,
                "english_affiliation": english_affiliation,
                "address": address,
                "personal_website": personal_website,
                "official_website": official_website,
                "google": google,
                "twitter": twitter,
                "facebook": facebook,
                "youtube": youtube,
                "gender": gender,
                "language": language
            }
        }
    }

    # 局部更新
    elasticsearch_connection.update_by_query(index=AUTHOR, body=update_body)

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'msg': 'success',
        'data': {}
    })
