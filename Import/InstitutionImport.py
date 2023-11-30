import os
import json
import time
import sys
import gzip
from tqdm import tqdm
from datetime import datetime
from elasticsearch_dsl import connections, Document, Integer, Keyword, Text, Nested, Double
from elasticsearch.helpers import parallel_bulk


class InstitutionDocument(Document):
    id = Keyword()
    cited_by_count = Integer()
    display_name = Text()
    homepage_url = Text()
    image_url = Text()
    lineage = Text(multi=True)
    ror = Keyword()
    type = Keyword()
    works_api_url = Text()
    works_count = Text()
    associated_institutions = Nested(
        properties={
            "id": Keyword(),
            "ror": Keyword(),
            "display_name": Keyword(),
            "country_code": Keyword(),
            "type": Keyword(),
            "relationship": Text(),
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
            "city": Text(),
            "geonames_city_id": Keyword(),
            "region": Text(),
            "country_code": Keyword(),
            "country": Text(),
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

    class Index:
        name = 'institution'
        settings = {
            'number_of_shards': 5,
            'number_of_replicas': 0,
        }


def run(client, file_name):
    with gzip.open(file_name, 'rt', encoding='utf-8') as file:
        i = 0
        data_list = []
        print("start indexing file {}".format(file_name))
        start_time = time.perf_counter()
        for line in file:
            data = json.loads(line)
            properties_to_extract = ["id", "cited_by_count", "display_name", "homepage_url", "image_url", "lineage", "ror", "type",
                                     "works_api_url", "works_count", "associated_institutions", "counts_by_year", "geo", "summary_stats"]
            data = {key: data.get(key) for key in properties_to_extract}
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
    cl = connections.create_connection(hosts=['localhost'])
    InstitutionDocument.init()
    print('日志路径', os.path.join(os.path.dirname(os.path.abspath(__file__)), "InstitutionImport.log"))

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "InstitutionImport.log"), 'w', encoding="utf-8") as file:
        print("Start insert to ElasticSearch at {}".format(datetime.now()))
        original_stdout = sys.stdout
        sys.stdout = file
        root_path = 'J:\\openalex-snapshot\\data\\institutions'
        # 获取所有子文件夹
        sub_folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))][0:10]
        for sub_folder in tqdm(sub_folders):
            folder_path = os.path.join(root_path, sub_folder)
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            for zip_file in files:
                file_name = os.path.join(folder_path, zip_file)
                run(cl, file_name)
        sys.stdout = original_stdout
        print("Finished insert to Elasticsearch at{}".format(datetime.now()))
