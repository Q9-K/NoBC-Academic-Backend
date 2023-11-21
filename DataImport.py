import json
import requests

url = 'http://localhost:9200/scholar/_bulk'
i = 1
file_path = 'J:/data' + '/new_data' + str(i) + '.json'
new_jsonfile = open(file_path, 'w')
with open("J:/mag_authors_0/mag_authors_2.txt","r") as fp:
    index = 1
    index1 = 1
    for line in fp:
        json_data = json.loads(line)
        id1 = json_data['id']
        new_data = {
            'index': {'_type': '_doc',
                      '_id': index1 },
        }
        index = index + 1
        index1 = index1 + 1
        if index % 5000 == 0:
            print('circle' + str(i))
            new_jsonfile.close()
            with open(file_path, 'r') as file:
                bulk_data = file.read()
            file_path = 'J:/data' + '/new_data' + str(i) + '.json'
            log_path = 'J:/logs' + '/log' + str(i) + '.txt'
            new_jsonfile = open(file_path, 'w')
            response = requests.post(url, data=bulk_data, headers={'Content-Type': 'application/x-ndjson'})
            if response.status_code != 200:
                print('error'+str(i))
            with open(log_path, 'w') as file1:
                # file1.write(str(response.status_code))
                file1.write(response.text)
            i = i + 1
        temp = json.dumps(new_data)
        new_jsonfile.write(temp)
        new_jsonfile.write('\n')
        # old_data = {'id': 'author.author.' + str(id1), 'django_ct': 'author.author', 'django_id': str(id1)}
        if len(json_data['name']) == 0 or json_data['name'] is None:
            print(json_data)
        old_data = {'name': json_data['name']}
        temp = json.dumps(old_data)
        new_jsonfile.write(temp)
        new_jsonfile.write('\n')

new_jsonfile.close()
