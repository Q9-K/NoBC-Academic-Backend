import json
import os
import gzip
from datetime import datetime
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Date, Float, Boolean, Completion, \
    Object
from elasticsearch.helpers import parallel_bulk
from elasticsearch import Elasticsearch
from path import data_path
from collections import deque

connections.create_connection(hosts=['localhost'], timeout=120, http_auth=('elastic', 'buaaNOBC2121'))
client = Elasticsearch(hosts=['localhost'], timeout=120, http_auth=('elastic', 'buaaNOBC2121'))
INDEX_NAME = 'work'


class WorkDocument(Document):
    id = Keyword()
    title = Text(analyzer='ik_max_word', search_analyzer='ik_smart', fields={
        'suggestion': Completion(analyzer='ik_max_word')
    })
    authorships = Nested(
        properties={
            "author": Object(
                properties={
                    "id": Keyword(),
                    "display_name": Text(
                        fields={
                            'keyword': Keyword()
                        }),
                    "orcid": Keyword()
                }
            ),
            "author_position": Keyword(index=False),
            "countries": Keyword(index=False),
            "institutions": Nested(
                properties={
                    "country_code": Keyword(),
                    "display_name": Text(
                        fields={
                            'keyword': Keyword()
                        }),
                    "id": Keyword(),
                    "lineage": Text(),
                    "ror": Text(),
                    "type": Keyword(),
                }
            )
        }
    )
    corresponding_author_ids = Keyword()
    corresponding_institution_ids = Keyword()
    cited_by_count = Integer()
    concepts = Nested(
        properties={
            "id": Keyword(),
            "wikidata": Keyword(index=False),
            "display_name": Text(
                fields={
                    'keyword': Keyword()
                }
            ),
            "level": Integer(),
            "score": Float()
        }
    )
    counts_by_year = Nested(
        properties={
            "year": Integer(),
            "works_count": Integer(),
            "cited_by_count": Integer(),
        }
    )
    language = Keyword()
    type = Keyword()
    publication_date = Date()
    referenced_works = Keyword(index=False)
    related_works = Keyword(index=False)
    abstract = Text(analyzer='ik_max_word', search_analyzer='ik_smart')
    locations = Nested(
        properties={
            "is_oa": Boolean(),
            "landing_page_url": Keyword(index=False),
            "pdf_url": Keyword(index=False),
            "source": Nested(
                properties={
                    "id": Keyword(),
                    "display_name": Text(
                        fields={
                            'keyword': Keyword()
                        }
                    ),
                    "issn_l": Keyword(index=False),
                    "issn": Keyword(index=False),
                    "host_organization": Keyword(index=False),
                    "type": Keyword(index=False),
                }
            ),
            "license": Keyword(index=False),
            "version": Keyword(index=False),
        }
    )
    visit_count = Integer()

    class Index:
        name = INDEX_NAME
        settings = {
            'number_of_shards': 20,
            'number_of_replicas': 0,
            'index': {
                'mapping.nested_objects.limit': 100000,
                'refresh_interval': -1,
                'translog': {
                    'durability': 'async',
                    'sync_interval': '120s',
                    'flush_threshold_size': '1024mb'
                }
            },
        }


def generate_actions(file_name):
    with gzip.open(file_name, 'rt', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            data = json.loads(line)
            properties_to_extract = ["id",
                                     "title",
                                     "authorships",
                                     "cited_by_count",
                                     "concepts",
                                     "counts_by_year",
                                     "language",
                                     "type",
                                     "publication_date",
                                     "referenced_works",
                                     "related_works",
                                     "locations",
                                     "corresponding_author_ids",
                                     "corresponding_institution_ids",
                                     ]
            abstract = data.get('abstract_inverted_index')
            data = {key: data[key] for key in properties_to_extract}
            data['visit_count'] = 0
            data['abstract'] = None
            if abstract:
                positions = [(word, pos) for word, pos_list in abstract.items() for pos in pos_list]
                positions.sort(key=lambda x: x[1])
                data['abstract'] = ' '.join([word for word, _ in positions])
            document = {
                '_index': INDEX_NAME,
                '_source': data
            }
            yield document


def run(file_name):
    actions = generate_actions(file_name)
    deque(parallel_bulk(client=client, actions=actions,
                        thread_count=8, queue_size=50,
                        chunk_size=1000, request_timeout=120
                        ), maxlen=0)


def process_files(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    for file in files:
        run(os.path.join(folder, file))


if __name__ == "__main__":

    WorkDocument.init()

    start_time = datetime.now()
    print("Start insert to ElasticSearch at {}".format(start_time))
    root_path = data_path + 'works'
    # 获取所有子文件夹
    sub_folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]

    for sub_folder in sub_folders:
        folder_path = os.path.join(root_path, sub_folder)
        process_files(folder_path)
    end_time = datetime.now()
    print("Finished insert to Elasticsearch at{}".format(end_time))
    print("cost time {}".format(end_time - start_time))
