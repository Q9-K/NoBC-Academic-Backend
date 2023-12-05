from pprint import pprint

from elasticsearch_dsl import Search, connections, Q

from NoBC.status_code import *
from config import ELAS_HOST
from utils.Response import response

# Create your views here.

# 创建es连接
ES_NAME = 'institution'
ES_CONN = connections.create_connection(alias=ES_NAME, hosts=[ELAS_HOST], timeout=20)


def pagination(search, request) -> Search:
    """
    分页查询,将基础查询语句进行分页处理,返回具有分页功能的查询语句
    :param request: 请求对象
    :param search: Search对象
    :return: Search对象
    """
    size = int(request.GET.get('size', 10))
    last_sort = request.GET.getlist('last_sort', None)
    page = int(request.GET.get('page', 1))
    _from = (page - 1) * size
    # 不需要after,使用(from, size)查询
    if last_sort is None:
        _from = (page - 1) * size
        ret = search[_from: size]
    # 使用search_after查询
    else:
        after_body = {
            'search_after': last_sort,
            'size': size
        }
        ret = search.update_from_dict(after_body)
    return ret


def get_return_data(search: Search, name: str) -> dict:
    """
    获取返回数据
    :param name: 返回数据的名称
    :param search: Search对象
    :return: 返回数据data
    """
    ret = search.execute().to_dict()['hits']['hits']
    data = []
    for ele in ret:
        dic = ele['_source']
        dic['sort'] = ele['sort']
        data.append(dic)
    return_data = dict()
    return_data['total'] = search.count()
    return_data[name] = data
    return return_data


def getInstitutionList(request):
    """
    获取机构列表
    :param request: {method: GET, params: {size: int, last_sort: array}}
                    其中last_sort为上一页最后一个数据的sort字段
    :return: {code: int, msg: str, data: [{}, {}]}
    """
    if request.method == 'GET':
        # 获取参数,使用search_after分页,需要获取:
        # 每页大小size,上一页最后一个数据的sort字段(若为"",默认为第一页)
        institutions = []
        # 默认id升序
        search = Search(using=ES_CONN, index='institution').query(Q('match_all')).sort('id')
        # 不需要after,使用(from, size)查询
        pagination_search = pagination(search, request)
        data = get_return_data(pagination_search, 'institutions')
        return response(SUCCESS, '查询成功', data)
    else:
        return response(METHOD_ERROR, '请求方式错误', error=True)


def getInstitutionDetail(request):
    """
    获取机构详情
    :param request: {method: GET, params: {id: int}}
    :return: {code: int, msg: str, data: {}}
    """
    if request.method == 'GET':
        # 获取参数,需要id
        institution_id = request.GET.get('id', "")
        if institution_id == "":
            return response(PARAMS_ERROR, '参数错误')
        # 查询
        search = Search(using=ES_CONN, index='institution').query('term', id=institution_id)
        ret = search.execute().to_dict()['hits']['hits']
        if len(ret) == 0:
            return response(ELASTIC_ERROR, '未找到该机构', error=True)
        else:
            return response(SUCCESS, '查询成功', ret[0]['_source'])
    else:
        return response(METHOD_ERROR, '请求方式错误', error=True)


def getInstitutionByKeyword(request):
    """
    根据关键词查询机构
    :param request: {method: GET, params: {keyword: str, size: int, last_sort: array}}
                    其中last_sort为上一页最后一个数据的sort字段
    :return: {code: int, msg: str, data: [{}, {}]}
    """
    if request.method == 'GET':
        # 获取参数,使用search_after分页,需要获取:
        # 每页大小size,上一页最后一个数据的sort字段(若为"",默认为第一页)
        keyword = request.GET.get('keyword', "")
        # 默认id升序
        search = Search(using=ES_CONN, index='institution').query('match', display_name=keyword).sort('id')
        pagination_search = pagination(search, request)
        data = get_return_data(pagination_search, 'institutions')
        return response(SUCCESS, '查询成功', data)
    else:
        return response(METHOD_ERROR, '请求方式错误', error=True)
