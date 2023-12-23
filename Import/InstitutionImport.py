import os
import json
import time
import gzip

from elasticsearch import Elasticsearch
from tqdm import tqdm
from datetime import datetime
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Double
from elasticsearch.helpers import parallel_bulk
from path import data_path

connections.create_connection(hosts=['localhost'], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))
client = Elasticsearch(hosts=['localhost'], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))


class InstitutionDocument(Document):
    id = Keyword()
    cited_by_count = Integer()
    display_name = Text(analyzer='english', search_analyzer='english')
    homepage_url = Keyword(index=False)
    image_url = Keyword(index=False)
    lineage = Keyword(index=False)
    ror = Keyword()
    type = Keyword()
    works_api_url = Keyword(index=False)
    works_count = Integer()
    associated_institutions = Nested(
        properties={
            "id": Keyword(),
            "ror": Keyword(),
            "display_name": Text(),
            "country_code": Keyword(),
            "type": Keyword(),
            "relationship": Keyword(),
        }
    )
    counts_by_year = Nested(
        properties={
            "year": Integer(),
            "works_count": Integer(),
            "cited_by_count": Integer(),
        }
    )
    geo = Nested(
        properties={
            "city": Keyword(),
            "geonames_city_id": Keyword(),
            "region": Keyword(),
            "country_code": Keyword(),
            "country": Keyword(),
            "latitude": Double(),
            "longitude": Double(),
        }
    )
    summary_stats = Nested(
        properties={
            "2yr_mean_citedness": Double(),
            "h_index": Integer(),
            "i10_index": Integer()
        }
    )
    chinese_display_name = Text(analyzer='ik_smart', search_analyzer='ik_smart')
    repositories = Nested(
        properties={
            'id': Keyword(),
            'display_name': Text()
        }
    )

    class Index:
        name = 'institution'
        settings = {
            'number_of_shards': 5,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'my_edge_ngram_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'my_edge_ngram_tokenizer'
                    }
                },
                'tokenizer': {
                    'my_edge_ngram_tokenizer': {
                        'type': 'edge_ngram',
                        'min_gram': 2,
                        'max_gram': 10,
                    }
                }
            }
        }


def run(client, file_name):
    with gzip.open(file_name, 'rt', encoding='utf-8') as file:
        i = 0
        data_list = []
        print("start indexing file {}".format(file_name))
        start_time = time.perf_counter()
        for line in file:
            origin_data = json.loads(line)
            properties_to_extract = ["id", "cited_by_count", "display_name", "homepage_url", "lineage",
                                     "ror", "type",
                                     "works_api_url", "works_count", "associated_institutions", "counts_by_year", "geo",
                                     "summary_stats", 'image_url']
            data = {key: origin_data.get(key) for key in properties_to_extract}
            international = origin_data.get('international', None)
            data['chinese_display_name'] = ''
            if international:
                display_name = international.get('display_name', None)
                if display_name:
                    data['chinese_display_name'] = display_name.get('zh-cn', None)
                    if not data['chinese_display_name']:
                        data['chinese_display_name'] = display_name.get('zh', None)
                        if not data['chinese_display_name']:
                            data['chinese_display_name'] = display_name.get('zh_hans', '')
            # 截取repositories
            repositories = origin_data.get('repositories', None)
            data['repositories'] = []
            repositories_list = []
            if repositories:
                for repository in repositories:
                    repositories_list.append({'id': repository['id'], 'display_name': repository['display_name']})
                data['repositories'] = repositories_list
            if data.get('id'):
                i += 1
                data_list.append({
                    "_op_type": "index",
                    "_index": "institution",
                    "_id": data.get('id'),
                    "_source": data
                })
            if i % 5000 == 0:
                start_time1 = time.time()
                for ok, response in parallel_bulk(client=client, actions=data_list, chunk_size=5000):
                    if not ok:
                        print(response)
                data_list = []
                end_time1 = time.time()
                print("circle {} process time = {}s".format(int(i / 5000), end_time1 - start_time1))
        if data_list:
            start_time1 = time.time()
            i += 1
            for ok, response in parallel_bulk(client=client, actions=data_list, chunk_size=5000):
                if not ok:
                    print(response)
            end_time1 = time.time()
            print("circle {} process time = {}s".format(int(i / 5000), end_time1 - start_time1))
        end_time = time.perf_counter()
        print(
            "finished indexing file {} process time= {} min, end at {}".format(file_name, (end_time - start_time) / 60,
                                                                               datetime.now()))


if __name__ == "__main__":
    InstitutionDocument.init()
    # print('日志路径', os.path.join(os.path.dirname(os.path.abspath(__file__)), "InstitutionImport.log"))
    #
    # with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "InstitutionImport.log"), 'w', encoding="utf-8") as file:
    print("Start insert to ElasticSearch at {}".format(datetime.now()))
    # original_stdout = sys.stdout
    # sys.stdout = file
    root_path = data_path + 'institutions'
    # 获取所有子文件夹
    sub_folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
    for sub_folder in tqdm(sub_folders):
        folder_path = os.path.join(root_path, sub_folder)
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        for zip_file in files:
            file_name = os.path.join(folder_path, zip_file)
            run(client, file_name)
    # sys.stdout = original_stdout
    print("Finished insert to Elasticsearch at{}".format(datetime.now()))
