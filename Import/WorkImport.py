import json
import logging
import os
import gzip
import random
from datetime import datetime
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Date, Completion, Object
from elasticsearch.helpers import parallel_bulk
from elasticsearch import Elasticsearch
from path import data_path
from collections import deque

connections.create_connection(hosts=['localhost'], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))
client = Elasticsearch(hosts=['localhost'], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))
INDEX_NAME = 'work'


class WorkDocument(Document):
    id = Keyword()
    title = Text(analyzer='ik_max_word', search_analyzer='ik_smart', fields={
        'suggestion': Completion(analyzer='ik_max_word')
    })
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
        }
    )
    authorships = Nested(
        properties={
            "author": Object(
                properties={
                    "id": Keyword(),
                    "display_name": Text(
                        fields={
                            'keyword': Keyword()
                        }),
                }
            ),
            "institutions": Nested(
                properties={
                    "display_name": Text(
                        fields={
                            'keyword': Keyword()
                        }),
                    "id": Keyword(),
                    "type": Keyword(index=False),
                }
            ),
            "country": Keyword(index=False),
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
            "landing_page_url": Keyword(index=False),
            "pdf_url": Keyword(index=False),
            "source": Object(
                properties={
                    "id": Keyword(),
                    "display_name": Text(
                        fields={
                            'keyword': Keyword()
                        }
                    ),
                    "host_organization": Keyword(index=False),
                    "host_organization_name": Keyword(index=False),
                    "type": Keyword(index=False),
                }
            ),
        }
    )
    corresponding_institution_ids = Keyword()
    visit_count = Integer()

    class Index:
        name = INDEX_NAME
        settings = {
            'number_of_shards': 16,
            'number_of_replicas': 0,
            'index': {
                # 'mapping.nested_objects.limit': 100000,
                'refresh_interval': '30s',
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
                                     "corresponding_institution_ids",
                                     ]
            abstract = data.get('abstract_inverted_index')
            data = {key: data.get(key) for key in properties_to_extract}
            # 提取id
            data['id'] = data['id'][len('https://openalex.org/'):]
            # 提取authorships
            authorships = []
            for authorship in data['authorships'][0:10]:
                properties_to_extract = ["author", "institutions", "countries"]
                authorship = {key: authorship.get(key) for key in properties_to_extract}
                authorship["author"] = {
                    "id": authorship["author"]["id"][len('https://openalex.org/'):] if authorship["author"].get(
                        'id') else None,
                    "display_name": authorship["author"]["display_name"],
                }
                institutions = []
                for institution in authorship["institutions"]:
                    institution = {
                        "id": institution["id"][len('https://openalex.org/'):],
                        "display_name": institution["display_name"],
                        "type": institution["type"],
                    }
                    institutions.append(institution)
                authorship["institutions"] = institutions
                authorship["country"] = authorship["countries"][0] if authorship.get("countries") else None
                authorship.pop("countries")
                authorships.append(authorship)
            data["authorships"] = authorships
            # 处理concepts
            concepts = []
            for concept in data["concepts"][0:10]:
                concept = {
                    "id": concept["id"][len('https://openalex.org/'):] if concept.get('id') else None,
                    "wikidata": concept["wikidata"],
                    "display_name": concept["display_name"],
                    "level": concept["level"],
                }
                concepts.append(concept)
            data["concepts"] = concepts
            # 设置pdf_url
            pdf_url = None
            for location in data["locations"]:
                if location.get("pdf_url"):
                    pdf_url = location.get("pdf_url")
                    break
            data["pdf_url"] = pdf_url
            # 处理locations
            locations = []
            for location in data["locations"][0:10]:
                location = {
                    "source": location["source"],
                    "landing_page_url": location["landing_page_url"],
                }
                source = location["source"]
                if source:
                    source = {
                        "id": source["id"][len('https://openalex.org/'):] if source.get('id') else None,
                        "display_name": source["display_name"],
                        "host_organization": source["host_organization"][len('https://openalex.org/'):]
                        if source.get('host_organization') else None,
                        "host_organization_name": source["host_organization_name"],
                        "type": source["type"],
                    }
                    location["source"] = source
                locations.append(location)
            data['locations'] = locations
            # 设置vist_count
            data['visit_count'] = random.randint(50, 10000)
            data['abstract'] = None
            if abstract:
                positions = [(word, pos) for word, pos_list in abstract.items() for pos in pos_list]
                positions.sort(key=lambda x: x[1])
                data['abstract'] = ' '.join([word for word, _ in positions])

            # 处理related_works和referenced_works
            related_works = []
            for related_work in data['related_works'][0:10]:
                related_works.append(related_work[len('https://openalex.org/'):])
            data['related_works'] = related_works
            referenced_works = []
            for referenced_work in data['referenced_works'][0:10]:
                referenced_works.append(referenced_work[len('https://openalex.org/'):])
            data['referenced_works'] = referenced_works
            corresponding_institution_ids = []
            for corresponding_institution_id in data["corresponding_institution_ids"][0:10]:
                corresponding_institution_id = corresponding_institution_id[len('https://openalex.org/'):]
                corresponding_institution_ids.append(corresponding_institution_id)
            data['corresponding_institution_ids'] = corresponding_institution_ids
            document = {
                '_index': INDEX_NAME,
                '_source': data,
                '_id': data['id'],
            }
            yield document


def run(file_name):
    actions = generate_actions(file_name)
    deque(parallel_bulk(client=client, actions=actions, request_timeout=60), maxlen=0)
    save_imported_files(file_name)


def process_files(folder):
    imported_files = get_imported_files()
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    for file in files:
        if os.path.join(folder, file) not in imported_files:
            run(os.path.join(folder, file))
        else:
            print(os.path.join(folder, file) + ' has been imported!')


def save_imported_files(file_name):
    with open('imported_files.txt', 'a') as file:
        file.write(file_name + '\n')


def get_imported_files():
    if not os.path.exists('imported_files.txt'):
        return set()

    with open('imported_files.txt', 'r') as file:
        return set(line.strip() for line in file)


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
