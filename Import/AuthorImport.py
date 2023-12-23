import os
import json
import gzip
from datetime import datetime
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Object, Float
from elasticsearch.helpers import parallel_bulk
from elasticsearch import Elasticsearch
from path import data_path

connections.create_connection(hosts=['localhost'], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))
client = Elasticsearch(hosts=['localhost'], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))


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
    summary_stats = Object(
        properties={
            "2yr_mean_citedness": Float(),
            "h_index": Integer(),
            "i10_index": Integer(),
            "oa_percent": Float(),
            "works_count": Integer(),
            "cited_by_count": Integer(),
            "2yr_works_count": Integer(),
            "2yr_cited_by_count": Integer(),
            "2yr_i10_index": Integer(),
            "2yr_h_index": Integer()
        }
    )
    last_known_institution = Object(
        properties={
            "id": Keyword(),
            "ror": Keyword(index=False),
            # "display_name": Text(),
            "display_name": Keyword(),
            "country_code": Keyword(),
            "type": Keyword(index=False)
        }
    )
    x_concepts = Nested(
        properties={
            "id": Keyword(),
            "wikidata": Keyword(index=False),
            "display_name": Keyword(),
            "level": Integer(),
            "score": Float()
        }
    )

    # 额外维护的信息
    user_id = Keyword()

    education_background = Text()
    personal_summary = Text()
    work_experience = Text()

    avatar = Keyword(index=False)
    chinese_name = Keyword()
    title = Keyword(index=False)
    phone = Keyword(index=False)
    fax = Keyword(index=False)
    email = Keyword(index=False)
    address = Keyword(index=False)
    personal_website = Keyword(index=False)
    official_website = Keyword(index=False)
    google = Keyword(index=False)
    twitter = Keyword(index=False)
    facebook = Keyword(index=False)
    youtube = Keyword(index=False)
    gender = Keyword(index=False)
    language = Keyword(index=False)

    class Index:
        name = 'author'
        settings = {
            'number_of_shards': 5,
            'number_of_replicas': 0,
            'index': {
                'mapping.nested_objects.limit': 100000,
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
            properties_to_extract = ["id", "cited_by_count", "counts_by_year", "display_name",
                                     "works_count", "summary_stats", "last_known_institution", "x_concepts"]
            data = {key: data[key] for key in properties_to_extract}

            x_concepts = []
            for x_concept in data['x_concepts'][0:10]:
                properties_to_extract = ["id", "wikidata", "display_name", "level", "score"]
                x_concept = {key: x_concept[key] for key in properties_to_extract}
                x_concepts.append(x_concept)
            data['x_concepts'] = x_concepts

            properties_to_manual_set = ["user_id", "education_background", "personal_summary", "work_experience",
                                        "avatar", "chinese_name", "title", "phone", "fax", "email", "address",
                                        "personal_website", "official_website", "google", "twitter", "facebook",
                                        "youtube", "gender", "language"]

            for key in properties_to_manual_set:
                data[key] = None

            # 设置默认头像
            # data['avatar'] = "http://nobc.buaa-q9k.xyz/default_author.png?e=1703243365&token=yMU1x7iZW8SmH14FmEP0sjoG1yflO_NJKtsoOGwk:yxy22yLr7nhjKf6hJCUf77hmFB8="

            document = {
                '_index': 'author',
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
    ScholarDocument.init()
    start_time = datetime.now()
    print("Start insert to ElasticSearch at {}".format(datetime.now()))
    root_path = data_path + 'authors'
    # 获取所有子文件夹
    sub_folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
    for sub_folder in sub_folders:
        folder_path = os.path.join(root_path, sub_folder)
        process_files(folder_path)
    end_time = datetime.now()
    print("Finished insert to Elasticsearch at{}".format(end_time))
    print("cost time {}".format(end_time - start_time))
