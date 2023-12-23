import os
import json
import time
import gzip
from tqdm import tqdm
from datetime import datetime
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Object, Double, Date
from elasticsearch.helpers import parallel_bulk
from elasticsearch import Elasticsearch
from path import data_path

connections.create_connection(hosts=['localhost'], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))
client = Elasticsearch(hosts=['localhost'], timeout=60, http_auth=('elastic', 'buaaNOBC2121'))
INDEX_NAME = 'source'


class SourceDocument(Document):
    id = Keyword()
    cited_by_count = Integer()
    counts_by_year = Nested(
        properties={
            "year": Integer(),
            "works_count": Integer(),
            "cited_by_count": Integer(),
        }
    )
    # display_name = Text(analyzer='ik_smart', search_analyzer='ik_smart')
    display_name = {
        "type": "text",  # 使用 text 类型进行分词
        "fields": {
            "keyword": {
                "type": "keyword"  # 使用 keyword 类型存储原始值，不分词
            }
        }
    },
    homepage_url = Keyword(index=False)
    host_organization = Keyword(index=False)
    host_organization_lineage = Keyword(index=False)
    host_organization_name = Text(analyzer='my_edge_ngram_analyzer', search_analyzer='my_edge_ngram_analyzer')
    summary_stats = Object(
        properties={
            "2yr_mean_citedness": Double(),
            "h_index": Integer(),
            "i10_index": Integer(),
        }
    )
    type = Keyword()
    created_date = Date()
    updated_date = Date()
    works_count = Integer()
    # 添加字段
    x_concepts = Nested(
        properties={
            "id": Keyword(),
            "wikidata": Keyword(),
            "display_name": Text(analyzer='my_edge_ngram_analyzer', search_analyzer='my_edge_ngram_analyzer'),
            "level": Integer(),
            "score": Double(),
        }
    )
    img_url = Keyword(index=False)

    class Index:
        name = 'source'
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
            data = json.loads(line)
            properties_to_extract = ["id", "cited_by_count", "counts_by_year", "display_name", "homepage_url",
                                     "host_organization", "host_organization_lineage", "host_organization_name",
                                     "summary_stats", "type", "societies", "created_date", "updated_date",
                                     "works_count", "x_concepts", "img_url"]
            data = {key: data.get(key) for key in properties_to_extract}
            if data.get('id'):
                i += 1
                data_list.append({
                    "_op_type": "index",
                    "_index": "source",
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
    SourceDocument.init()
    # print('日志路径', os.path.join(os.path.dirname(os.path.abspath(__file__)), "SourceImport.log"))

    # with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "SourceImport.log"), 'w', encoding='utf-8') as file:
    print("Start insert to ElasticSearch at {}".format(datetime.now()))
    # original_stdout = sys.stdout
    # sys.stdout = file
    root_path = data_path + 'sources'
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
