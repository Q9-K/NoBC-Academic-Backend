from elasticsearch_dsl.connections import connections

elasticsearch_connection = connections.get_connection()


# 根据id获取作者的所有作品，不分页就获取全部
def es_get_works(author_id, page_num=-1, page_size=-1):
    query_body = {
        "query": {
            'nested': {
                'path': 'authorships',
                'query': {
                    'term': {
                        'authorships.author.id': author_id
                    }
                }
            }
        }
    }
    # 分页
    if page_num != -1 and page_size != -1:
        query_body['from'] = (page_num - 1) * page_size
        query_body['size'] = page_size
    res = elasticsearch_connection.search(index='work', body=query_body)
    return res


# 根据id获取作者信息
def es_get_author_by_id(author_id):
    query_body = {
        "query": {
            "term": {
                "id": author_id
            }
        }
    }
    res = elasticsearch_connection.search(index='author', body=query_body)
    return res
