from pprint import pprint
# Create your views here.
from django.http import JsonResponse
from elasticsearch_dsl import connections, Search
from elasticsearch_dsl.query import Match, Term, Q, MultiMatch, Query, Range
from NoBC.status_code import *
from utils.view_decorator import allowed_methods
import requests

elasticsearch_connection = connections.get_connection()
INDEX_NAME = 'work'


@allowed_methods(['GET'])
def search(request):
    query_content = request.GET.get('query_content')
    time_from = request.GET.get('time_from')
    time_to = request.GET.get('time_to')
    journal = request.GET.get('journal')
    subject = request.GET.get('subject')
    institution = request.GET.get('institution')

    if not query_content:
        return JsonResponse({
            'code': PARAMS_ERROR,
            'error': True,
            'message': 'please input search text.',
            'data': {}
        })
    search = Search(using=elasticsearch_connection, index=INDEX_NAME).highlight('title', fragment_size=50)
    # if common search
    match = MultiMatch(query=query_content, fields=['abstract', 'title'])
    search = search.query(match)
    # if has time range
    if time_from and time_to:
        time_range = Range()
        search = search.query(time_range)
    # TODO
    if journal:
        pass
    # TODO
    if subject:
        pass
    # TODO
    if institution:
        pass
    search = search.source(['title', 'abstract', 'authorships', 'best_oa_location'])
    search_results = search.execute()
    results = []
    pprint(search_results['hits']['hits'])
    for hit in search_results:
        results.append(hit.to_dict())
    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'OK',
        'data': {
            'count': len(results),
            'results': results
        },
    })


@allowed_methods(['GET'])
def get_work(request):
    ip = get_client_ip(request)
    request = request.GET
    id = request.get('id')
    search = Search(using=elasticsearch_connection, index=INDEX_NAME)
    search = search.filter('term', id=id)
    result = search.execute()
    return JsonResponse({
        'code': SUCCESS,
        'error': False,
        'message': 'OK',
        'data': {
            'count': 0,
            'results': {}
        }
    })



@allowed_methods(['GET'])
def get_popular_work(request):
    search = Search(using=elasticsearch_connection)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_reply(request):
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
    os.environ["OPENAI_API_KEY"] = "sk-ep0kiIljEZTRfRax8b259aC21cD34d6596Ab4dCfAbAaF894"

    os.environ["OPENAI_API_BASE"] = "https://api.132999.xyz/v1"

    # 根据文件类型来定义一个loader，不同的loader能够解析不同的文件内容，最终都会解析为一个大文本
    destination_file = "./currentPDF.pdf"
    download_webpage(url, destination_file)
    loader = PyPDFLoader(destination_file)

    # 定义文本分块的规则，这里用了一个很简单的规则，按照默认的分隔符来切割文本，使得每一段不超过1000个字符
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = loader.load_and_split(splitter)

    # 定义文本的embedding，也就是如何把文本转换为向量。默认使用sentence-transformers这个免费的模型，也可以使用OpenAI提供的收费接口
    embeddings = OpenAIEmbeddings()

    # 实现一个本地的文档语义搜索，在存入一堆chunk之后，能够随时检索和问题最相关的一些chunk。Chroma就是一个比较流行的vector store
    db = Chroma.from_documents(chunks, embeddings)

    # 本地搜索到的chunk会作为context，和问题一起提交给LLM来处理。我们当然要使用ChatGPT模型了，比GPT-3.0又好又便宜
    llm = ChatOpenAI(temperature=0)

    # chain是LangChain里的概念，其实就相当于定义了一个流程，这里我们提供的参数就是文档语义搜索工具以及LLM
    chain = RetrievalQA.from_chain_type(llm, retriever=db.as_retriever())

    reply = chain(msg)

    # 下面就比较简单了，不断读取问题然后执行chain
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
            file.write(response.content)
    except requests.exceptions.RequestException as e:
        print("error")