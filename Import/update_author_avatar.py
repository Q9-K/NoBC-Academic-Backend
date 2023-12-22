from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections

from config import ELAS_HOST
from utils.get_scholar_avatar import get_scholar_avatar

connections.create_connection(hosts=[ELAS_HOST], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))
client = Elasticsearch(hosts=[ELAS_HOST], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))
def get_authors_with_high_h_index(index_name, client, h_index_threshold=4):
    # 创建一个查询对象
    search = Search(using=client, index=index_name)

    # 定义查询条件：h_index 大于 h_index_threshold
    query = Q("range", summary_stats__h_index={"gt": h_index_threshold})

    # 应用查询并执行搜索
    search = search.query(query)
    response = search.execute()

    # 返回结果中的 ScholarDocument 实例
    return [hit for hit in response]



def update_avatars_for_authors(scholars):
    for scholar in scholars:
        # 检查 h_index 是否大于 30
        if scholar.summary_stats.h_index > 4:
            if not scholar.avatar:
                # 尝试获取头像
                print({scholar.display_name, scholar.last_known_institution.display_name})
                avatar_url = get_scholar_avatar(scholar.display_name, scholar.last_known_institution.display_name)
                print(1)
                # 如果获取到头像，更新 scholar 的 avatar 属性
                if avatar_url:
                    scholar.avatar = avatar_url


scholars = get_authors_with_high_h_index('author', client)

# 然后你可以使用之前提到的 update_avatars_for_scholars 函数来更新头像
update_avatars_for_authors(scholars)