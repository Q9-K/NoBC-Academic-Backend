# -*- coding:utf-8 -*-

from elasticsearch import Elasticsearch

from elasticsearch_dsl.connections import connections

from config import ELAS_HOST


connections.create_connection(hosts=[ELAS_HOST], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))
client = Elasticsearch(hosts=[ELAS_HOST], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))

def update():
    #先查找concept索引中指定的id，然后更新chinese_display_name为我要的值
    print(client.update(index='concept', id='https://openalex.org/C2524010', body={'doc': {'chinese_description': '研究形状、大小、图形的相对位置等的数学分支'}}))

    #然后查找这个id，看看更新是否成功

if __name__ == '__main__':
    update()
