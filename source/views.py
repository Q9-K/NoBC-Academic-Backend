from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from elasticsearch_dsl import connections, Search, Q
from NoBC.status_code import *
import json
import threading

elasticsearch_connection = connections.get_connection()
SOURCE_INDEX = 'source'
# WORK_INDEX = 'work_optimized'
WORK_INDEX = 'work'


def get_source_by_id(request):
    if request.method == 'GET':
        source_id = request.GET.get('source_id')
        query_body = {
            "query": {
                "match": {
                    "id": source_id,
                }
            },
            "_source": ["display_name", "cited_by_count", "counts_by_year", "works_count", "summary_stats", "x_concepts", "created_date"]
        }
        es_res = elasticsearch_connection.search(index=SOURCE_INDEX, body=query_body)
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


def get_source_list(request):
    if request.method == 'GET':
        initial = request.GET.get('initial')
        #subjects = request.GET.getlist('subject', [])
        subjects_json = request.GET.get('subject', '[]')
        subjects = json.loads(subjects_json)
        #host_organization_name = request.GET.get('host_organization_name')
        page_num = int(request.GET.get('page_num', 1))
        page_size = int(request.GET.get('page_size', 10))

        search = Search(using=elasticsearch_connection, index=SOURCE_INDEX)
        #if subjects and host_organization_name:
        #    query = (
        #        Q("prefix", display_name__keyword=initial) &
        #        Q("nested", path="x_concepts", query=Q("terms", **{"x_concepts.display_name": subjects2})) &
        #        Q("match", host_organization_name=host_organization_name)
        #    )
        #    search = search.query(query)
        # print(len(subjects2))
        # elif host_organization_name:
        #    query = (
        #        Q("prefix", display_name__keyword=initial) &
        #        Q("match", host_organization_name=host_organization_name)
        #    )
        #    search = search.query(query)
        if len(subjects) != 0:
            query = (
                Q("prefix", display_name__keyword=initial) &
                Q("nested", path="x_concepts", query=Q("terms", **{"x_concepts.display_name": subjects}))
            )
            search = search.query(query)
        else:
            query = Q("prefix", display_name__keyword=initial)
            search = search.query(query)

        search = search[(page_num - 1) * page_size:(page_num - 1) * page_size + page_size - 1]
        es_res = search.execute()

        res = []
        for hit in es_res:
            hit = hit.to_dict()
            res.append({
                'id': hit['id'],
                'display_name': hit['display_name'],
                'x_concepts': hit['x_concepts'],
                'summary_stats': hit['summary_stats'],
                'host_organization_name': hit['host_organization_name']
            })
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
        es_res = elasticsearch_connection.search(index=SOURCE_INDEX, body=query_body)
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


def get_latest_sources(request):
    if request.method == 'GET':
        page_num = int(request.GET.get('page_num', 1))
        page_size = int(request.GET.get('page_size', 10))
        subjects_json = request.GET.get('subject', '[]')
        subjects = json.loads(subjects_json)
        # print(subjects)
        if len(subjects) != 0:
            query_body = {
                "query": {
                    "nested": {
                        "path": "x_concepts",
                        "query": {
                            "terms": {
                                "x_concepts.display_name": subjects
                            }
                        }
                    }
                },
                "sort": [
                    {
                        "updated_date": {
                            "order": "desc",
                        }
                    }
                ],
                "_source": ["id", "display_name", "x_concepts", "summary_stats", "updated_date"],
                "from": (page_num - 1) * page_size,
                "size": page_size
            }
        else:
            query_body = {
                "query": {
                    "match_all": {}
                },
                "sort": [
                    {
                        "updated_date": {
                            "order": "desc",
                        }
                    }
                ],
                "_source": ["id", "display_name", "x_concepts", "summary_stats", "updated_date"],
                "from": (page_num - 1) * page_size,
                "size": page_size
            }
        es_res = elasticsearch_connection.search(index=SOURCE_INDEX, body=query_body)
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


def get_works_by_cited(request):
    if request.method == 'GET':
        id = request.GET.get("source_id")
        source_id = id.split('/')[-1]
        query_body = {
            "query": {
                "nested": {
                    "path": "locations",
                    "query": {
                        "term": {
                            "locations.source.id": {
                                "value": source_id
                            }
                        }
                    }
                }
            },
            "sort": [
                {
                    "cited_by_count": {
                        "order": "desc",
                    }
                }
            ],
            "_source": ["id", "title", "cited_by_count"],
            "size": 20
        }

        es_res = elasticsearch_connection.search(index=WORK_INDEX, body=query_body)
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
        id = request.GET.get("source_id")
        source_id = id.split('/')[-1]

        query_body = {
            "size": 10,
            "query": {
                "nested": {
                    "path": "locations",
                    "query": {
                        "term": {
                            "locations.source.id": {
                                "value": source_id
                            }
                        }
                    }
                }
            },
            "aggs": {
                "all_authors": {
                    "nested": {
                        "path": "authorships"
                    },
                    "aggs": {
                        "composite_authors": {
                            "composite": {
                                "size": 10000,
                                "sources": [
                                    {"id": {"terms": {"field": "authorships.author.id"}}},
                                    {"display_name": {"terms": {"field": "authorships.author.display_name.keyword"}}}
                                ]
                            },
                            "aggs": {
                                "reverse_nested_cited_by_count": {
                                    "reverse_nested": {},
                                    "aggs": {
                                        "total_cited_by_count": {
                                            "sum": {
                                                "field": "cited_by_count"
                                            }
                                        }
                                    }
                                },
                                "sorted_authors": {
                                    "bucket_sort": {
                                        "sort": [
                                            {
                                                "reverse_nested_cited_by_count>total_cited_by_count.value": {
                                                    "order": "desc"
                                                }
                                            }
                                        ],
                                        "size": 20
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        es_res = elasticsearch_connection.search(index=WORK_INDEX, body=query_body)
        res = es_res["aggregations"]["all_authors"]["composite_authors"]["buckets"]
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


def get_institutions_by_cited(request):
    if request.method == 'GET':
        id = request.GET.get("source_id")
        source_id = id.split('/')[-1]

        query_body = {
            "size": 10,
            "query": {
                "nested": {
                    "path": "locations",
                    "query": {
                        "term": {
                            "locations.source.id": {
                                "value": source_id
                            }
                        }
                    }
                }
            },
            "aggs": {
                "all_institutions": {
                    "nested": {
                        "path": "authorships.institutions"
                    },
                    "aggs": {
                        "institutions_composite": {
                            "composite": {
                                "size": 1000,
                                "sources": [
                                    {"id": {"terms": {"field": "authorships.institutions.id"}}},
                                    {"display_name": {"terms": {"field": "authorships.institutions.display_name.keyword"}}}
                                ]
                            },
                            "aggs": {
                                "reverse_nested_cited_by_count": {
                                    "reverse_nested": {},
                                    "aggs": {
                                        "total_cited_by_count": {
                                            "sum": {
                                                "field": "cited_by_count"
                                            }
                                        }
                                    }
                                },
                                "sorted_authors": {
                                    "bucket_sort": {
                                        "sort": [
                                            {
                                                "reverse_nested_cited_by_count>total_cited_by_count.value": {
                                                    "order": "desc"
                                                }
                                            }
                                        ],
                                        "size": 20
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        es_res = elasticsearch_connection.search(index=WORK_INDEX, body=query_body)
        res = es_res["aggregations"]["all_institutions"]["institutions_composite"]["buckets"]
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
        id = request.GET.get("source_id")
        source_id = id.split('/')[-1]
        query_body1 = {
            "size": 10,
            "query": {
                "nested": {
                    "path": "locations",
                    "query": {
                        "term": {
                            "locations.source.id": {
                                "value": source_id
                            }
                        }
                    }
                }
            },
            "aggs": {
                "institutions": {
                    "nested": {
                        "path": "authorships.institutions"
                    },
                    "aggs": {
                        "institutions_composite": {
                            "composite": {
                                "size": 10000,
                                "sources": [
                                    {"id": {"terms": {"field": "authorships.institutions.id"}}},
                                    {"display_name": {
                                        "terms": {"field": "authorships.institutions.display_name.keyword"}}}
                                ]
                            },
                            "aggs": {
                                "doc_count_sort": {
                                    "bucket_sort": {
                                        "sort": [{"_count": {"order": "desc"}}],
                                        "size": 20
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        es_res1 = elasticsearch_connection.search(index=WORK_INDEX, body=query_body1)
        query_body2 = {
            "size": 10,
            "query": {
                "nested": {
                    "path": "locations",
                    "query": {
                        "term": {
                            "locations.source.id": {
                                "value": source_id
                            }
                        }
                    }
                }
            },
            "aggs": {
                "countrys": {
                    "nested": {
                        "path": "authorships"
                    },
                    "aggs": {
                        "works_by_country": {
                            "terms": {
                                "field": "authorships.country",
                                "size": 10000,
                                "script": {
                                    "source": "doc['authorships.country'].value",
                                    "lang": "painless"
                                }
                            },
                            "aggs": {
                                "doc_count_sort": {
                                    "bucket_sort": {
                                        "sort": [{"_count": {"order": "desc"}}],
                                        "size": 20
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        es_res2 = elasticsearch_connection.search(index=WORK_INDEX, body=query_body2)

        res = []
        # res.append(es_res1["aggregations"]["institutions"]["institutions_composite"]["buckets"])
        # res.append(es_res2["aggregations"]["countrys"]["works_by_country"]["buckets"])
        es_institution = es_res1["aggregations"]["institutions"]["institutions_composite"]["buckets"]
        institution = []
        others = 0
        for i in range(len(es_institution)):
            if i < 10:
                institution.append(es_institution[i])
            else:
                others += es_institution[i]["doc_count"]
        institution.append({"key": {"id": "", "display_name": "others"}, "doc_count": others})
        res.append(institution)
        es_country = es_res2["aggregations"]["countrys"]["works_by_country"]["buckets"]
        country = []
        others = 0
        for i in range(len(es_country)):
            if i < 10:
                country.append(es_country[i])
            else:
                others += es_country[i]["doc_count"]
        country.append({"key": "others", "doc_count": others})
        res.append(country)

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
        es_res = elasticsearch_connection.search(index=SOURCE_INDEX, body=query_body)
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
        es_res = elasticsearch_connection.search(index=SOURCE_INDEX, body=query_body)
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
