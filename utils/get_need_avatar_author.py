from elasticsearch_dsl.connections import connections
from config import *

es = connections.create_connection(hosts=[ELAS_HOST], timeout=60, http_auth=(ELAS_USER, ELAS_PASSWORD))

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

# 深度分页
scroll = es.search(
    index="author",
    scroll="1m",
    size=100,
    body=query_body
)

# 获取总数
total = scroll["hits"]["total"]
print("total: ", total)
