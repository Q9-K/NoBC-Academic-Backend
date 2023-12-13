from elasticsearch_dsl.connections import connections

elasticsearch_connection = connections.get_connection()


# 获取作者作品
def es_get_works(author_id):
    query_body = {
        "query": {
            'nested': {
                'path': 'authorships',
                'query': {
                    'nested': {
                        'path': 'authorships.author',
                        'query': {
                            'term': {
                                'authorships.author.id': author_id
                            }
                        }
                    }
                }
            }
        }
    }
    res = elasticsearch_connection.search(index='work', body=query_body)
    return res


# 获取作者信息
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
