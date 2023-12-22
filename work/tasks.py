# tasks.py
from celery import shared_task
from django.core.cache import cache
import redis

@shared_task
def update_es():
    # 连接到Redis
    r = redis.Redis(host='localhost', port=6379, db=0)

    # 设置匹配模式
    match_pattern = 'visit*'

    # 初始化游标
    cursor = '0'
    print('11')
    while True:
        cursor, keys = r.scan(cursor=cursor, match=match_pattern)
        for key in keys:
            value = r.get(key)  # 获取键的值
            print(f'Key: {key}, Value: {value}'+'111111')
            r.delete(key)  # 删除键

        # 当游标返回0时，表示遍历结束
        if cursor == '0':
            break