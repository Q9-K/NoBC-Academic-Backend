import names
import requests
import os
url = 'http://100.92.185.118:8000/scholar/search/'
file_path = os.path.join(os.path.dirname(__file__), 'test.log')
print(file_path)
with open(file_path, "w", encoding="utf-8") as file:
    # data = file.readlines()
    # for line in data:
    for line in range(0, 500):
        name = names.get_full_name()
        file.write("name="+name+' ')
        # print("name="+name,end=' ')
        response = requests.get(url=url, params={'text': name})
        response_json = response.json()
        time = float(response_json['took'])
        time = time*1000
        file.write("time="+str(time)+'ms\n')
        # print('time='+str(time)+'ms')
        if time > 1000:
            print("over time!")
