# Create your views here.

import numpy as np
import requests
from django.core.cache import cache
from elasticsearch_dsl import connections, Search
from elasticsearch_dsl.query import Q, MultiMatch

from config import OPENAI_API_KEY
from utils.view_decorator import *

elasticsearch_connection = connections.get_connection()
INDEX_NAME = 'work_optimized'
page_size = 10
min_score_threshold = 10.0


@allowed_methods(['GET'])
def search(request):
    content = request.GET.get('content')
    order_by = request.GET.get('order_by')
    order_term = request.GET.get('order_term')
    page_number = request.GET.get('page_number')

    if not content:
        return JsonResponse({
            'code': PARAMS_ERROR,
            'error': True,
            'message': 'please input search text.',
            'data': {}
        })
    search = Search(using=elasticsearch_connection, index=INDEX_NAME)
    match = MultiMatch(query=content, fields=['abstract', 'title'])
    search = search.query(match)
    if order_by:
        sort_by = None
        if order_by == 'default':
            sort_by = '_score'
        if order_by == 'cited_by_count':
            sort_by = 'cited_by_count'
        elif order_by == 'time':
            sort_by = 'publication_date'
        if order_term == 'asc':
            sort_by = '-' + sort_by
        search = search.sort(sort_by)
    search = search.highlight('title', 'abstract')
    search = search.source(['publication_date', 'type', 'language',
                            'visit_count', 'cited_by_count', 'id',
                            'authorships', 'abstract', 'title', 'locations'])
    if page_number:
        page_number = int(page_number)
        search = search[(page_number - 1) * page_size:(page_number - 1) * page_size + page_size - 1]
    # pprint(search.to_dict())
    search = search.params(min_score=min_score_threshold)
    search.aggs.bucket('publication_dates', 'date_histogram', field='publication_date', calendar_interval='1y')
    search.aggs.bucket('authors', 'nested', path='authorships').bucket(
        'top_authors', 'terms', field='authorships.author.id', size=10, order={'_count': 'desc'}  # 指定降序排序
    ).bucket('author_info', 'top_hits', size=1)
    search.aggs.bucket('concepts', 'nested', path='concepts').bucket(
        'top_concepts', 'terms', field='concepts.id', size=10, order={'_count': 'desc'}
    ).bucket('concept_info', 'top_hits', size=1)
    search.aggs.bucket('authorships', 'nested', path='authorships').bucket(
        'institutions', 'nested', path='authorships.institutions'
    ).bucket('top_institutions', 'terms', field='authorships.institutions.id', size=10,
             order={'_count': 'desc'}).bucket(
        'institution_info', 'top_hits', size=1
    )
    search.aggs.bucket('locations', 'nested', path='locations').bucket(
        'sources', 'nested', path='locations.source'
    ).bucket('top_sources', 'terms', field='locations.source.id', size=10,
             order={'_count': 'desc'}).bucket('source_info', 'top_hits', size=1)
    response = search.execute()
    publication_dates = response.aggregations.publication_dates.buckets[-10:]
    top_authors = response.aggregations.authors.top_authors.buckets
    top_concepts = response.aggregations.concepts.top_concepts.buckets
    top_institutions = response.aggregations.authorships.institutions.top_institutions.buckets
    top_sources = response.aggregations.locations.sources.top_sources.buckets
    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'OK',
        'data': {
            'count': search.count(),
            'data': [{
                'highlight': hit.meta.highlight.to_dict(),
                'other': {
                    **hit.to_dict(),
                    'citation': get_citation(hit.to_dict()),
                }

            } for hit in response],
            'statistics': {
                'docs_by_year': [{
                    'doc_count': bucket['doc_count'],
                    'year': bucket['key_as_string'][0:4],
                } for bucket in publication_dates],
                'top_authors': [
                    {
                        'id': bucket.key,
                        'display_name': bucket.author_info.hits.hits[0]._source['author'][
                            'display_name'],
                        'doc_count': bucket.doc_count,
                    }
                    for bucket in top_authors
                ],
                'top_concepts': [
                    {
                        'id': bucket.key,
                        'display_name': bucket.concept_info.hits.hits[0]._source['display_name'],
                        'doc_count': bucket.doc_count,
                    }
                    for bucket in top_concepts
                ],
                'top_institutions': [
                    {
                        'id': bucket.key,
                        'display_name': bucket.institution_info.hits.hits[0]._source['display_name'],
                        'doc_count': bucket.doc_count,
                    }
                    for bucket in top_institutions
                ],
                'top_sources': [
                    {
                        'id': bucket.key,
                        'display_name': bucket.source_info.hits.hits[0]._source['display_name'],
                        'doc_count': bucket.doc_count,
                    }
                    for bucket in top_sources
                ],
            }
        },
    })


@allowed_methods(['GET'])
def advanced_search(request):
    content = request.GET.get('content')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    source = request.GET.get('source')
    concept = request.GET.get('concept')
    institution = request.GET.get('institution')
    order_by = request.GET.get('order_by')
    order_term = request.GET.get('order_term')
    page_number = request.GET.get('page_number')

    if not content:
        return JsonResponse({
            'code': PARAMS_ERROR,
            'error': True,
            'message': 'please input search text.',
            'data': {}
        })
    search = Search(using=elasticsearch_connection, index=INDEX_NAME)

    match = MultiMatch(query=content, fields=['abstract', 'title'])
    search = search.query(match)

    if start_time or end_time:
        if start_time:
            time_range_1 = Q('range', publication_date={'gte': start_time})
            search = search.query(time_range_1)
        if end_time:
            time_range_2 = Q('range', publication_date={'lte': end_time})
            search = search.query(time_range_2)

    if source:
        query = Q("nested", path="locations",
                  query=Q("nested", path="locations.source",
                          query=Q("term", locations__source__id=source)))
        # query = Q("nested", path="locations",
        #           query=Q("match", locations__source__display_name=source))
        # print(query.to_dict())
        search = search.query(query)

    if concept:
        query = Q("nested", path="concepts",
                  query=Q("match", concepts__display_name=concept))
        search = search.query(query)

    if institution:
        query = Q("nested", path="authorships",
                  query=Q("nested", path="authorships.institutions",
                          query=Q('term', authorships__institutions__id=institution)))
        search = search.query(query)

    if order_by:
        sort_by = None
        if order_by == 'default':
            sort_by = '_score'
        if order_by == 'cited_by_count':
            sort_by = 'cited_by_count'
        elif order_by == 'time':
            sort_by = 'publication_date'

        if order_term == 'asc':
            sort_by = '-' + sort_by
        search = search.sort(sort_by)
    search = search.source(['publication_date', 'type', 'language',
                            'visit_count', 'cited_by_count', 'id',
                            'authorships', 'abstract', 'title', 'locations'])
    search = search.highlight('title', 'abstract')
    if page_number:
        page_number = int(page_number)
        search = search[(page_number - 1) * page_size:(page_number - 1) * page_size + page_size - 1]
    # pprint(search.to_dict())
    search = search.params(min_score=min_score_threshold)
    search.aggs.bucket('publication_dates', 'date_histogram', field='publication_date', calendar_interval='1y')
    search.aggs.bucket('authors', 'nested', path='authorships').bucket(
        'top_authors', 'terms', field='authorships.author.id', size=10, order={'_count': 'desc'}  # 指定降序排序
    ).bucket('author_info', 'top_hits', size=1)
    search.aggs.bucket('concepts', 'nested', path='concepts').bucket(
        'top_concepts', 'terms', field='concepts.id', size=10, order={'_count': 'desc'}
    ).bucket('concept_info', 'top_hits', size=1)
    search.aggs.bucket('authorships', 'nested', path='authorships').bucket(
        'institutions', 'nested', path='authorships.institutions'
    ).bucket('top_institutions', 'terms', field='authorships.institutions.id', size=10,
             order={'_count': 'desc'}).bucket(
        'institution_info', 'top_hits', size=1
    )
    search.aggs.bucket('locations', 'nested', path='locations').bucket(
        'sources', 'nested', path='locations.source'
    ).bucket('top_sources', 'terms', field='locations.source.id', size=10,
             order={'_count': 'desc'}).bucket('source_info', 'top_hits', size=1)
    response = search.execute()
    publication_dates = response.aggregations.publication_dates.buckets[-10:]
    top_authors = response.aggregations.authors.top_authors.buckets
    top_concepts = response.aggregations.concepts.top_concepts.buckets
    top_institutions = response.aggregations.authorships.institutions.top_institutions.buckets
    top_sources = response.aggregations.locations.sources.top_sources.buckets
    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'OK',
        'data': {
            'count': search.count(),
            'data': [{
                'highlight': hit.meta.highlight.to_dict(),
                'other': {
                    **hit.to_dict(),
                    'citation': get_citation(hit.to_dict()),
                }
            } for hit in response],
            'statistics': {
                'docs_by_year': [{
                    'doc_count': bucket['doc_count'],
                    'year': bucket['key_as_string'][0:4],
                } for bucket in publication_dates],
                'top_authors': [
                    {
                        'id': bucket.key,
                        'display_name': bucket.author_info.hits.hits[0]._source['author'][
                            'display_name'],
                        'doc_count': bucket.doc_count,
                    }
                    for bucket in top_authors
                ],
                'top_concepts': [
                    {
                        'id': bucket.key,
                        'display_name': bucket.concept_info.hits.hits[0]._source['display_name'],
                        'doc_count': bucket.doc_count,
                    }
                    for bucket in top_concepts
                ],
                'top_institutions': [
                    {
                        'id': bucket.key,
                        'display_name': bucket.institution_info.hits.hits[0]._source['display_name'],
                        'doc_count': bucket.doc_count,
                    }
                    for bucket in top_institutions
                ],
                'top_sources': [
                    {
                        'id': bucket.key,
                        'display_name': bucket.source_info.hits.hits[0]._source['display_name'],
                        'doc_count': bucket.doc_count,
                    }
                    for bucket in top_sources
                ],
            }
        },
    })


# @login_required
@allowed_methods(['GET'])
def get_work(request):
    user_id = request.GET.get('user_id')
    if user_id:
        id = request.GET.get('id')
        if cache.get(id) is None:
            search = Search(using=elasticsearch_connection, index=INDEX_NAME)
            search = search.filter('term', id=id)
            response = search.execute()
            if len(response.hits) > 0:
                data = [hit.to_dict() for hit in response][0]
                data['citation'] = get_citation(data)
                info = []
                for referenced_work in data['referenced_works']:
                    s = Search(using=elasticsearch_connection, index=INDEX_NAME)
                    s = s.filter('term', id=referenced_work)
                    res = s.execute()
                    if len(res.hits) > 0:
                        res = [hit.to_dict() for hit in res][0]
                        info.append({
                            'id': referenced_work,
                            'title': res['title'],
                            'cited_by_count': res['cited_by_count'],
                            'pdf_url': res['pdf_url'],
                        })
                data['referenced_works_info'] = info
                info = []
                for related_work in data['related_works']:
                    s = Search(using=elasticsearch_connection, index=INDEX_NAME)
                    s = s.filter('term', id=related_work)
                    res = s.execute()
                    if len(res.hits) > 0:
                        res = [hit.to_dict() for hit in res][0]
                        info.append({
                            'id': related_work,
                            'title': res['title'],
                            'cited_by_count': res['cited_by_count'],
                            'pdf_url': res['pdf_url']
                        })
                data['related_works_info'] = info
                data.pop('referenced_works', None)
                data.pop('related_works', None)
            else:
                data = {}
            cache.set(id, data, timeout=60 * 60)
        else:
            data = cache.get(id)
        key = 'visit_' + id
        if cache.get(key) is None:
            cache.set(key, set(user_id), timeout=60 * 60)
        else:
            visit_set = cache.get(key)
            if user_id not in visit_set:
                visit_set.add(user_id)
                cache.set(key, visit_set)
        return JsonResponse({
            'code': SUCCESS,
            'error': False,
            'message': 'OK',
            'data': {
                'count': 0 if data == {} else 1,
                'data': data
            }
        })
    else:
        return JsonResponse({
            'code': PARAMS_ERROR,
            'error': True,
            'message': 'please provide user_id.',
            'data': {}
        })


@allowed_methods(['GET'])
def get_popular_works(request):
    institution_id = request.GET.get('institution_id')
    concept_id = request.GET.get('concept_id')

    search = Search(using=elasticsearch_connection, index=INDEX_NAME)
    key = 'popular_works'
    if institution_id:
        key = key + '_' + institution_id
        nested_query = Q('term', corresponding_institution_ids=institution_id)
        search = search.query(nested_query)
    elif concept_id:
        key = key + '_' + concept_id
        nested_query = Q('nested', path='concepts', query=Q('term', concepts__id=concept_id))
        search = search.query(nested_query)
    if cache.get(key):
        data = cache.get(key)
    else:
        search = search.sort('-cited_by_count')
        search = search.source(['publication_date', 'visit_count', 'cited_by_count', 'id', 'title', 'authorships'])
        search = search.extra(size=200)
        response = search.execute()
        data = [hit.to_dict() for hit in response]
        cache.set(key, data, timeout=None)
    if data:
        data = weighted_random_choice(data)

    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'OK',
        'data': {
            'count': len(data),
            'data': data
        }
    })


@allowed_methods(['GET'])
def get_suggestion(request):
    content = request.GET.get('content')
    search = Search(using=elasticsearch_connection, index=INDEX_NAME)
    search = search.suggest('suggestion-work', content, completion={'field': 'title.suggestion'})
    search = search.source('title')
    response = search.execute()
    results = response.suggest['suggestion-work'][0]['options']
    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'OK',
        'data': {
            'suggestions': [result['text'] for result in results]
        }
    })


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


gpt = None


@allowed_methods(['GET'])
def get_reply(request):
    global gpt
    from langchain.chat_models import ChatOpenAI
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.document_loaders.pdf import PyPDFLoader
    from langchain.chains.retrieval_qa.base import RetrievalQA
    import os
    # 提示用户输入文件名，支持pdf文件和普通文本文件
    # file_path = input("input pdf path: ")
    msg = request.GET.get('msg', '')
    url = request.GET.get('pdf_url', '')
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    os.environ["OPENAI_API_BASE"] = "https://api.132999.xyz/v1"
    # 根据文件类型来定义一个loader
    destination_file = "./currentPDF.pdf"
    download_webpage(url, destination_file)
    loader = PyPDFLoader(destination_file)
    # 定义文本分块的规则
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = loader.load_and_split(splitter)
    # 定义文本的embedding，也就是如何把文本转换为向量
    embeddings = OpenAIEmbeddings()
    # 实现一个本地的文档语义搜索，在存入一堆chunk之后，能够随时检索和问题最相关的一些chunk
    db = Chroma.from_documents(chunks, embeddings)
    # 本地搜索到的chunk会作为context，
    llm = ChatOpenAI(temperature=0)
    # chain是LangChain里的概念，其实就相当于定义了一个流程，这里我们提供的参数就是文档语义搜索工具以及LLM
    chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())
    gpt = chain
    reply = chain(msg)
    # 返回结果
    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'OK',
        'data': {
            'reply': reply
        }
    })


def download_webpage(url, destination_file):
    try:
        # 发送GET请求获取网页内容
        response = requests.get(url)
        response.raise_for_status()  # 如果请求不成功，抛出异常
        # 将网页内容写入本地文件
        with open(destination_file, 'wb') as file:
            file.truncate()
            file.write(response.content)
    except requests.exceptions.RequestException as e:
        print(e)


@allowed_methods(['GET'])
def get_quick_reply(request):
    global gpt
    import os
    # 提示用户输入文件名，支持pdf文件和普通文本文件
    # file_path = input("input pdf path: ")
    msg = request.GET.get('msg', '')
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    os.environ["OPENAI_API_BASE"] = "https://api.132999.xyz/v1"
    reply = gpt(msg)
    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'OK',
        'data': {
            'reply': reply
        }
    })


def weighted_random_choice(weighted_works):
    # 提取权重和元素
    weights = np.array([work['cited_by_count'] for work in weighted_works])
    elements = np.array(weighted_works)

    # 计算累积权重
    cum_weights = np.cumsum(weights)

    # 从累积权重中进行随机选择
    chosen_indices = np.searchsorted(cum_weights, np.random.rand(10) * cum_weights[-1])

    # 返回选择的结果
    chosen_work = elements[chosen_indices]
    return chosen_work.tolist()


def get_citation(data):
    publication_date = data['publication_date']
    title = data['title']
    authorships = data['authorships']
    citation = (f"{', '.join(authorship['author']['display_name'] for authorship in authorships[0:3])} "
                f"({publication_date}). {title}.")
    return citation
