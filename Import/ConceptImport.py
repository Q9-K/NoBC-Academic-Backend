import os
import json
import time
import gzip
from tqdm import tqdm
from datetime import datetime
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Double, Object
from elasticsearch.helpers import parallel_bulk
from elasticsearch import Elasticsearch
from path import data_path

connections.create_connection(hosts=['localhost'], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))
client = Elasticsearch(hosts=['localhost'], timeout=60,http_auth=('elastic', 'buaaNOBC2121'))


class ConceptDocument(Document):
    id = Keyword()
    cited_by_count = Integer()
    counts_by_year = Nested(
        properties={
            "year": Integer(),
            "works_count": Integer(),
            "cited_by_count": Integer(),
        }
    )
    summary_stats = Object(
        properties={
            "2yr_mean_citedness": Double(),
            "h_index": Integer(),
            "i10_index": Integer(),
        }
    )
    level = Integer()
    display_name = Text(analyzer='my_edge_ngram_analyzer', search_analyzer='my_edge_ngram_analyzer')
    works_count = Integer()
    image_url = Keyword()
    ancestors = Nested(
        properties={
            "id": Keyword(),
            "display_name": Keyword(),
            "chinese_display_name": Keyword(),
            "level": Integer(),
            "score": Double(),
        }
    )
    related_concepts = Nested(
        properties={
            "id": Keyword(),
            "display_name": Keyword(),
            "chinese_display_name": Keyword(),
            "level": Integer(),
            "score": Double(),
        }
    )
    works_api_url = Text()
    chinese_display_name = Text(analyzer='ik_smart', search_analyzer='ik_smart')
    discription = Text()
    chinese_discription = Text()

    class Index:
        name = 'concept'
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


def run(file_name):
    with gzip.open(file_name, 'rt', encoding='utf-8') as file:
        i = 0
        data_list = []
        print("start indexing file {}".format(file_name))
        start_time = time.perf_counter()
        for line in file:
            data = json.loads(line)
            for ancestor in data.get('ancestors', []):
                ancestor['chinese_display_name'] = ''

             # 为 related_concepts 中的每个元素添加空的 chinese_display_name
            for related_concept in data.get('related_concepts', []):
                related_concept['chinese_display_name'] = ''
            international = data.get('international', {})
            data['chinese_display_name'] = ''
            data['description'] = ''
            data['chinese_description'] = ''
            if international:
                display_name = international.get('display_name')
                description = international.get('description')

                if display_name:
                    data['chinese_display_name'] = display_name.get('zh-cn','')
                if description:
                    data['description'] = description.get('en', '')
                    data['chinese_description'] = description.get('zh-cn')
                    if not data['chinese_description']:
                        data['chinese_description'] = description.get('zh')
                        if not data['chinese_description']:
                            data['chinese_description'] = description.get('zh-hans', '')
            properties_to_extract = ["id", "cited_by_count", "counts_by_year", "summary_stats", "level", "display_name",
                                     "works_count", "image_url", "ancestors",
                                     "related_concepts", "counts_by_year", "works_api_url", "chinese_display_name",
                                     "description", "chinese_description"]
            data = {key: data.get(key) for key in properties_to_extract}

            if data.get('id'):
                i += 1
                data_list.append({
                    "_op_type": "index",
                    "_index": "concept",
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
    ConceptDocument.init()
    # print('日志路径', os.path.join(os.path.dirname(os.path.abspath(__file__)), "AuthorImport.log"))
    #
    # with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "AuthorImport.log"), 'w',encoding='utf-8') as file:
    print("Start insert to ElasticSearch at {}".format(datetime.now()))
    # original_stdout = sys.stdout
    # sys.stdout = file
    root_path = data_path + 'concepts'
    # 获取所有子文件夹
    sub_folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
    for sub_folder in tqdm(sub_folders):
        folder_path = os.path.join(root_path, sub_folder)
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        for zip_file in files:
            file_name = os.path.join(folder_path, zip_file)
            run(file_name)
    # sys.stdout = original_stdout
    print("Finished insert to Elasticsearch at{}".format(datetime.now()))
