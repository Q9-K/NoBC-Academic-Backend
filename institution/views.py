from django.shortcuts import render
from utils.Response import response
from NoBC.commons import Commons
from config import ELAS_HOST
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, connections, Q, A

# Create your views here.

# 创建es连接
ES_NAME = 'institution'
ES_CONN = connections.create_connection(alias=ES_NAME, hosts=[ELAS_HOST], timeout=20)


def getInstitutionList(request):
    """
    获取机构列表
    :param request: {method: GET, params: {size: int, last_sort: array}}
                    其中last_sort为上一页最后一个数据的sort字段
    :return: {code: int, msg: str, data: [{}, {}]}
    """
    if request.method == 'GET':
        # 获取参数,使用search_after分页,需要获取:
        # 每页大小size,上一页最后一个数据的sort字段(若为0,默认为第一页)
        size = int(request.GET.get('size', 10))
        last_sort = request.GET.get('last_sort', None)
        data = []
        # 默认id升序
        search = Search(using=ES_CONN, index='institution').query(Q('match_all')).sort('id')
        # 不需要after,使用(from, size)查询
        if last_sort is None:
            ret = search[0: size]
        # 使用search_after查询
        else:
            after_body = {
                'search_after': last_sort,
                'size': size
            }
            ret = search.update_from_dict(after_body)
        for ele in ret.execute().to_dict()['hits']['hits']:
            dic = ele['_source']
            dic['sort'] = ele['sort']
            data.append(dic)
        return response(Commons.SUCCESS, '查询成功', data)
    else:
        return response(Commons.METHOD_ERROR, '请求方式错误')
