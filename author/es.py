from elasticsearch_dsl.connections import connections

elasticsearch_connection = connections.get_connection()

# 索引名映射
AUTHOR = 'author'
CONCEPT = 'concept'
INSTITUTION = 'institution'
SOURCE = 'source'
WORK = 'work_optimized'

prefix = "https://openalex.org/"


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
    else:
        query_body['from'] = 0
        query_body['size'] = 20
    res = elasticsearch_connection.search(index=WORK, body=query_body)
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
    res = elasticsearch_connection.search(index=AUTHOR, body=query_body)
    return res
