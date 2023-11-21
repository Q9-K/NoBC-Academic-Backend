import json
print(1)
# data = {
#     "67": [4],
#     "Despite": [0],
#     "growing": [1],
#     "interest": [2],
#     "in": [3, 5, 6, 7, 9],
#     "practice.": [8]
# }

with open('test.txt', 'r', encoding="utf-8") as file:
    content = file.read()
    data = json.loads(content)
    data = data.get('abstract_inverted_index')
    if data:
        positions = [(word, pos) for word, pos_list in data.items() for pos in pos_list]

        # 根据位置信息对字符串进行还原
        positions.sort(key=lambda x: x[1])
        restored_string = ' '.join([word for word, _ in positions])
        print(restored_string)
    else:
        print("no inverted index")
