import requests
import json
def get_scholar_avatar(name,school):
    # 定义 URL 和 POST 数据
    url = 'https://searchtest.aminer.cn/aminer-search/search/person'
    data = {
        "query": "",
        "needDetails": True,
        "page": 0,
        "size": 20,
        "searchKeyWordList": [{"advanced": True, "keyword": name, "operate": "0", "wordType": 4, "segmentationWord": "true", "needTranslate": True},{"advanced":True,"keyword":school,"operate":"0","wordType":5,"segmentationWord":"true","needTranslate":True}]
    }
    # 发送 POST 请求
    response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    response_json = response.json()
    print(response_json)
    # 从 JSON 数据中获取头像 URL
    hit_list = response_json['data'].get('hitList', [])

    # 检查 hit_list 是否有内容
    if hit_list:
        if hit_list[0].get('avatar', None):
            avatar_url = hit_list[0]['avatar']
        else:
            avatar_url = None
    else:
        avatar_url = None
    return avatar_url