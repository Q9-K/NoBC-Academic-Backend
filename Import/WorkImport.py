import json
import os
import gzip
from datetime import datetime
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Date, Float, Boolean
from elasticsearch.helpers import parallel_bulk


cl = connections.create_connection(hosts=['localhost'])


class WorkDocument(Document):
    id = Keyword()
    title = Text()
    authorships = Nested(
        properties={
            "author": Nested(
                properties={
                    "id": Keyword(),
                    "display_name": Keyword(),
                    "orcid": Keyword()
                }
            ),
            "author_position": Keyword(),
            "countries": Keyword()
        }
    )
    best_oa_location = Nested(
        properties={
            "is_oa": Boolean(),
            "landing_page_url": Keyword(),
            "pdf_url": Keyword(),
            "source": Nested(
                properties={
                    "id": Keyword(),
                    "display_name": Keyword(),
                    "issn_l": Keyword(),
                    "issn": Keyword(),
                    "host_organization": Keyword(),
                    "type": Keyword(),
                }
            ),
            "license": Keyword(),
            "version": Keyword(),
        })
    cited_by_count = Integer()
    concepts = Nested(
        properties={
            "id": Keyword(),
            "wikidata": Keyword(),
            "display_name": Keyword(),
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
    referenced_works = Keyword(multi=True)
    related_works = Keyword(multi=True)
    abstract = Text()

    class Index:
        name = 'work'
        settings = {
            'number_of_shards': 40,
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
            properties_to_extract = ["id", "title", "authorships", "best_oa_location",
                                     "cited_by_count", "concepts", "counts_by_year",
                                     "created_date", "language", "type", "publication_date",
                                     "referenced_works", "related_works"]
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
    for success, info in parallel_bulk(client=cl, actions=actions, thread_count=6, queue_size=6, chunk_size=5000):
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
