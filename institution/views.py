from elasticsearch_dsl import Search, connections, Q

from NoBC.status_code import *
from utils.Response import response
from config import ELAS_USER, ELAS_PASSWORD, ELAS_HOST

# Create your views here.

# 创建es连接,有密码
ES_NAME = 'institution'
ES_CONN = connections.create_connection(hosts=[ELAS_HOST], http_auth=(ELAS_USER, ELAS_PASSWORD), timeout=20)


def pagination(search, request) -> Search:
    """
    分页查询,将基础查询语句进行分页处理,返回具有分页功能的查询语句
    :param request: 请求对象
    :param search: Search对象
    :return: Search对象
    """
    size = int(request.GET.get('page_size', 10))
    last_sort = request.GET.getlist('last_sort', None)
    page = int(request.GET.get('page_num', 1))
    _from = (page - 1) * size
    # 不需要after,使用(from, size)查询
    if last_sort is None or len(last_sort) == 0:
        _from = (page - 1) * size
        ret = search[_from: _from + size]
    # 使用search_after查询
    else:
        after_body = {
            'search_after': last_sort,
            'size': size
        }
        ret = search.update_from_dict(after_body)
    return ret


def get_return_data(search: Search, data_name: str, key_list: [], deeper_name_list=None) -> dict:
    """
    获取返回数据
    :param data_name: 返回数据的名字
    :param deeper_name_list: 深层嵌套提取
    :param search: Search对象
    :param key_list 需要返回的字段
    :return: 返回数据 data: {total: int, name: [{}, {}]}
    """
    ret = search.execute().to_dict()['hits']['hits']
    data = []
    for ele in ret:
        origin_data = ele['_source']
        dic = dict()
        if len(key_list) == 0:
            dic = origin_data
        else:
            for key in key_list:
                dic[key] = origin_data[key]
                if origin_data[key] is None and key == 'image_url':
                    dic[key] = 'http://nobc.buaa-q9k.xyz/default_institution.png?e=1734783247&token=yMU1x7iZW8SmH14FmEP0sjoG1yflO_NJKtsoOGwk:J5FtwKmo6-5TeSMdTmUVBCec87s='
            if deeper_name_list:
                # 遍历需要深一层获取的名字
                for key in deeper_name_list.keys():
                    # 获取名字对应的数据,可能是数组,也可能是字典
                    deeper_origin_data = origin_data[key]
                    # 遍历需要获取的字段
                    # 是数组
                    if type(deeper_origin_data) is list:
                        tmp_list = []
                        for list_ele in deeper_origin_data:
                            tmp = dict()
                            for name in deeper_name_list[key]:
                                tmp[name] = list_ele[name]
                            tmp_list.append(tmp)
                        dic[key] = tmp_list
                    # 是字典
                    else:
                        dic[key] = dict()
                        for name in deeper_name_list[key]:
                            dic[key][name] = deeper_origin_data[name]
        data.append(dic)
    return_data = dict()
    return_data['total'] = search.count()
    return_data[data_name] = data
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
        # 默认id升序
        search = Search(using=ES_CONN, index='institution').query(Q('match_all')).sort('id')
        # 调用封装好的分页函数
        key_list = ['id', 'display_name', 'chinese_display_name', 'image_url', 'type']
        pagination_search = pagination(search, request)
        data = get_return_data(pagination_search, 'institutions', key_list)
        return response(SUCCESS, '查询成功', data)
    else:
        return response(METHOD_ERROR, '请求方式错误', error=True)


def getInstitutionDetail(request):
    """
    获取指定机构详情
    :param request: {method: GET, params: {id: int}} 其中id为指定机构的id
    :return: {code: int, msg: str, data: {}}
    """
    if request.method == 'GET':
        # 获取参数,需要id
        institution_id = request.GET.get('id', "")
        if institution_id == "":
            return response(PARAMS_ERROR, '参数错误')
        # 查询
        search = Search(using=ES_CONN, index='institution').query('term', id=institution_id)
        key_list = ['display_name', 'type', 'chinese_display_name', 'image_url', 'homepage_url',
                    'lineage', 'counts_by_year', 'repositories']
        deeper_name_map = {'associated_institutions': ['id', 'display_name'],
                           'geo': ['country_code', 'city']}
        ret = get_return_data(search, 'institution', key_list, deeper_name_map)
        if len(ret) == 0:
            return response(ELASTIC_ERROR, '未找到该机构', error=True)
        else:
            return response(SUCCESS, '查询成功', ret)
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
        keyword = request.GET.get('keyword', '')
        # 默认id升序
        # # 正则表达式匹配
        # query_body = (Q('regexp', display_name={'value': '.*' + keyword + '.*', 'flags': 'ALL'}) |
        #               Q('regexp', chinese_display_name={'value': '.*' + keyword + '.*', 'flags': 'ALL'}))
        # # 加上模糊搜索,fuzziness为容错率,默认为AUTO,
        # query_body = (query_body |
        #               Q('match', display_name={'query': keyword, 'fuzziness': 'AUTO'}) |
        #               Q('match', chinese_display_name={'query': keyword, 'fuzziness': 'AUTO'}))
        query_body = (Q('match', display_name={'query': keyword, 'fuzziness': 'AUTO'}) |
                      Q('match', chinese_display_name={'query': keyword, 'fuzziness': 'AUTO'}))
        search = Search(using=ES_CONN, index='institution').query(query_body).sort('id')
        pagination_search = pagination(search, request)
        key_list = ['id', 'display_name', 'chinese_display_name']
        data = get_return_data(pagination_search, 'institutions', key_list)
        return response(SUCCESS, '查询成功', data)
    else:
        return response(METHOD_ERROR, '请求方式错误', error=True)
