import json
import os
import gzip
from datetime import datetime
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Date, Float, Boolean
from elasticsearch.helpers import parallel_bulk
from elasticsearch import Elasticsearch

connections.create_connection(hosts=['localhost'], timeout=60)
client = Elasticsearch(hosts=['localhost'], timeout=60)


class WorkDocument(Document):
    id = Keyword()
    title = Text(analyzer='ik_smart', search_analyzer='ik_smart')
    authorships = Nested(
        properties={
            "author": Nested(
                properties={
                    "id": Keyword(),
                    "display_name": Text(),
                    "orcid": Keyword()
                }
            ),
            "author_position": Keyword(index=False),
            "countries": Keyword(index=False)
        }
    )
    best_oa_location = Nested(
        properties={
            "is_oa": Boolean(),
            "landing_page_url": Keyword(index=False),
            "pdf_url": Keyword(index=False),
            "source": Nested(
                properties={
                    "id": Keyword(),
                    "display_name": Text(),
                    "issn_l": Keyword(index=False),
                    "issn": Keyword(index=False),
                    "host_organization": Keyword(index=False),
                    "type": Keyword(index=False),
                }
            ),
            "license": Keyword(index=False),
            "version": Keyword(index=False),
        })
    cited_by_count = Integer()
    concepts = Nested(
        properties={
            "id": Keyword(),
            "wikidata": Keyword(index=False),
            "display_name": Text(),
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
    created_date = Date()
    language = Keyword()
    type = Keyword()
    publication_date = Date()
    referenced_works = Keyword(index=False)
    related_works = Keyword(index=False)
    abstract = Text(analyzer='ik_smart', search_analyzer='ik_smart')
    locations = Nested(
        properties={
            "is_oa": Boolean(),
            "landing_page_url": Keyword(index=False),
            "pdf_url": Keyword(index=False),
            "source": Nested(
                properties={
                    "id": Keyword(),
                    "display_name": Text(),
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

    class Index:
        name = 'work'
        settings = {
            'number_of_shards': 40,
            'number_of_replicas': 0,
            'index': {
                'mapping.nested_objects.limit': 100000,
                'refresh_interval': -1,
                'translog': {
                    'durability': 'async',
                    'sync_interval': '30s',
                    'flush_threshold_size': '1024mb'
                }
            },
        }


def generate_actions(file_name):
    with gzip.open(file_name, 'rt', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            data = json.loads(line)
            properties_to_extract = ["id", "title", "authorships", "best_oa_location",
                                     "cited_by_count", "concepts", "counts_by_year",
                                     "created_date", "language", "type", "publication_date",
                                     "referenced_works", "related_works", "locations"]
            abstract = data.get('abstract_inverted_index')
            data = {key: data[key] for key in properties_to_extract}
            data['abstract'] = None
            if abstract:
                positions = [(word, pos) for word, pos_list in abstract.items() for pos in pos_list]
                positions.sort(key=lambda x: x[1])
                data['abstract'] = ' '.join([word for word, _ in positions])
            document = {
                '_index': 'work',
                '_op_type': 'index',
                '_source': data
            }
            yield document


def run(file_name):
    actions = generate_actions(file_name)
    for success, info in parallel_bulk(client=client, actions=actions, thread_count=8, queue_size=8, chunk_size=5000):
        if not success:
            print(f'Failed to index document: {info}')


def process_files(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    for file in files:
        run(os.path.join(folder, file))


if __name__ == "__main__":

    WorkDocument.init()

    start_time = datetime.now()
    print("Start insert to ElasticSearch at {}".format(start_time))
    root_path = '/data/openalex-snapshot/data/works'
    # 获取所有子文件夹
    sub_folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]

    for sub_folder in sub_folders:
        folder_path = os.path.join(root_path, sub_folder)
        process_files(folder_path)
    end_time = datetime.now()
    print("Finished insert to Elasticsearch at{}".format(end_time))
    print("cost time {}".format(end_time - start_time))
