# 获取h-index>20的学者列表，结果输出到scholar_list.json
from elasticsearch_dsl.connections import connections

elasticsearch_connection = connections.get_connection()

# 从es中获取h-index>20的学者列表
query_body = {
    "query": {
        "bool": {
            "must": [
                {
                    "range": {
                        "indices.h_index": {
                            "gte": 20
                        }
                    }
                }
            ]
        }
    }
}

for i in range(0, 10000, 100):
    es_res = elasticsearch_connection.search(index='author', body=query_body)
    pass
