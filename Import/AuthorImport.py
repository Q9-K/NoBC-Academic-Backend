import os
import json
import gzip
from datetime import datetime
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested
from elasticsearch.helpers import parallel_bulk
from elasticsearch import Elasticsearch

connections.create_connection(hosts=['localhost'], timeout=60)
client = Elasticsearch(hosts=['localhost'], timeout=60)

class ScholarDocument(Document):
    id = Keyword()
    cited_by_count = Integer()
    counts_by_year = Nested(
        properties={
            "year": Integer(),
            "works_count": Integer(),
            "cited_by_count": Integer(),
        }
    )
    display_name = Text(analyzer='ik_smart', search_analyzer='ik_smart')
    works_count = Integer()
    last_known_institution = Nested(
        properties={
            "id": Keyword(),
            "ror": Keyword(index=False),
            "display_name": Text(),
            "country_code": Keyword(),
            "type": Keyword(index=False),
            "lineage": Keyword(index=False)
        }
    )
    user_id = Keyword()

    class Index:
        name = 'author'
        settings = {
            'number_of_shards': 5,
            'number_of_replicas': 0,
            'index.mapping.nested_objects.limit': 200000,
            'index.refresh_interval': -1,
            'index.translog.durability': 'async',
            'index.translog.sync_interval': '300s',
            'index.translog.flush_threshold_size': '512mb',
        }


def generate_actions(file_name):
    with gzip.open(file_name, 'rt', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            data = json.loads(line)
            properties_to_extract = ["id", "cited_by_count", "counts_by_year", "display_name",
                                     "works_count", "last_known_institution"]
            data = {key: data[key] for key in properties_to_extract}
            data['user_id'] = None
            document = {
                '_index': 'author',
                '_op_type': 'index',
                '_source': data
            }
            yield document


def run(file_name):
    actions = generate_actions(file_name)
    for success, info in parallel_bulk(client=client, actions=actions, thread_count=6, queue_size=6, chunk_size=5000):
        if not success:
            print(f'Failed to index document: {info}')


def process_files(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    for file in files:
        run(os.path.join(folder, file))


if __name__ == "__main__":
    ScholarDocument.init()
    start_time = datetime.now()
    print("Start insert to ElasticSearch at {}".format(datetime.now()))
    root_path = '/data/openalex-snapshot/data/authors'
    # 获取所有子文件夹
    sub_folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
    for sub_folder in sub_folders:
        folder_path = os.path.join(root_path, sub_folder)
        process_files(folder_path)
    end_time = datetime.now()
    print("Finished insert to Elasticsearch at{}".format(end_time))
    print("cost time {}".format(end_time - start_time))
