# Create your views here.
import base64
import json
import random
import sys
from pprint import pprint
from django.http import JsonResponse
from elasticsearch_dsl import connections, Search, UpdateByQuery
from elasticsearch_dsl.query import Match, Term, Q, MultiMatch, Query, Range
from NoBC.status_code import *
from utils.view_decorator import *
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from config import OPENAI_API_KEY
import requests
from django_redis import get_redis_connection
import numpy as np

redis_conn = get_redis_connection("default")
elasticsearch_connection = connections.get_connection()
INDEX_NAME = 'work_optimized'
page_size = 10
min_score_threshold = 10.0
sys.stdout.reconfigure(encoding='utf-8')


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
    response = search.execute()
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
                    'citation': get_citation(hit.to_dict())
                }

            } for hit in response]
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
        # query = Q("nested", path="locations",
        #           query=Q("nested", path="locations.source",
        #                   query=Q("match", locations__source__display_name=source)))
        query = Q("nested", path="locations",
                  query=Q("match", locations__source__display_name=source))
        # print(query.to_dict())
        search = search.query(query)

    if concept:
        query = Q("nested", path="concepts",
                  query=Q("match", concepts__display_name=concept))
        search = search.query(query)

    if institution:
        query = Q("nested", path="authorships",
                  query=Q("nested", path="authorships.institutions",
                          query=Q('match', authorships__institutions__display_name=institution)))
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
    response = search.execute()
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
                    'citation': get_citation(hit.to_dict),
                }
            } for hit in response]
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
            cache.set(id, data, 60 * 60)
        else:
            data = cache.get(id)
        # ip = get_client_ip(request)
        # params = {'id': id, 'user_id': user_id, 'ip': ip}
        key = 'visit_' + id
        if cache.get(key) is None:
            # update_by_query = UpdateByQuery(using=elasticsearch_connection, index=INDEX_NAME)
            # update_by_query = update_by_query.filter('term', id=id)
            # update_by_query = update_by_query.script(source="ctx._source.visit_count++", lang='painless')
            # update_by_query.execute()
            cache.set(key, set(user_id), 60 * 60)
        else:
            visit_set = cache.get(key)
            if user_id not in visit_set:
                # update_by_query = UpdateByQuery(using=elasticsearch_connection, index=INDEX_NAME)
                # update_by_query = update_by_query.filter('term', id=id)
                # update_by_query = update_by_query.script(source="ctx._source.visit_count++", lang='painless')
                # update_by_query.execute()
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
    citation = (f"{', '.join(authorship['author']['display_name'] for authorship in authorships)} "
                f"({publication_date}). {title}.")
    return citation
