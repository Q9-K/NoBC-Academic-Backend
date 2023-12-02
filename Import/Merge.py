import os
import json
import time
import gzip
from tqdm import tqdm
from datetime import datetime
from elasticsearch_dsl import connections, Search
from elasticsearch.helpers import parallel_bulk
import pandas as pd

def run(client, file_name, index_name):
    with gzip.open(file_name, 'rt', encoding='utf-8') as file:
        i = 0
        data_list = []
        print("start handling file {}".format(file_name))
        start_time = time.perf_counter()
        csv_reader = pd.read_csv(file_name, compression='gzip')
        print(csv_reader.shape[0])
        for index, row in csv_reader.iterrows():
            i += 1
            from_id = "https://openalex.org/"+row['id']
            data_list.append(from_id)
            if i % 5000 == 0:
                start_time1 = time.time()
                query = {
                    "query": {
                        "terms": {
                            "_id": data_list
                        }
                    }
                }
                search = Search(using=client, index=index_name).update_from_dict(query)
                response = search.delete()
                if response.deleted > 0:
                    print(f"Successfully deleted {response.deleted} documents.")
                data_list = []
                end_time1 = time.time()
                print("circle {} process time = {}s".format(int(i / 5000), end_time1 - start_time1))
        if data_list:
            start_time1 = time.time()
            query = {
                "query": {
                    "terms": {
                        "_id": data_list
                    }
                }
            }
            search = Search(using=client, index=index_name).update_from_dict(query)
            response = search.delete()
            if response.deleted > 0:
                print(f"Successfully deleted {response.deleted} documents.")
            data_list = []
            end_time1 = time.time()
            print("circle {} process time = {}s".format(int(i / 5000), end_time1 - start_time1))
        end_time = time.perf_counter()
        print("finished handling file {} process time= {} min, end at {}"
              .format(file_name, (end_time - start_time) / 60, datetime.now()))

if __name__ == "__main__":
    cl = connections.create_connection(hosts=['localhost'])
    print("Start merge data at {}".format(datetime.now()))
    root_path = '/data/openalex-snapshot/data/merged_ids'
    sub_folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
    for sub_folder in tqdm(sub_folders):
        folder_path = os.path.join(root_path, sub_folder)
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        for zip_file in files:
            file_name = os.path.join(folder_path, zip_file)
            # print(sub_folder)
            run(cl, file_name, index_name=sub_folder[:-1])
    print("Finished merge data at{}".format(datetime.now()))
