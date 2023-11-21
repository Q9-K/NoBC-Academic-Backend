import heapq
from celery import shared_task
from django.core.cache import cache

@shared_task
def sort_and_cache_results(results, base_cache_key):
    # 快速找到得分最高的5个结果
    #top_5_results = heapq.nlargest(5, results, key=lambda x: x['n_citation'])

    #取前五个
    top_5_results = results[0:5]

    # 将前5个结果存储在缓存中，以便客户端可以快速访问
    cache.set(f'{base_cache_key}_page_1', top_5_results)

    # 将剩余的排序任务放回消息队列
    get_remaining_results.apply_async(args=[results, top_5_results, base_cache_key])

    #返回待排序结果的个数
    return top_5_results
@shared_task
def get_remaining_results(results,top_results,base_cache_key):
    remaining_results = [result for result in results if result not in top_results]

    sort_remaining_results.apply_async(args=[remaining_results, base_cache_key])


@shared_task
def sort_remaining_results(remaining_results, base_cache_key):
    # 对剩余的结果进行排序
    sorted_remaining_results = sorted(remaining_results, key=lambda x: x['n_citation'], reverse=True)

    # 将完全排序的结果按页存储在缓存中
    for i in range(0, len(sorted_remaining_results), 5):
        page_number = i // 5 + 2  # +2 代表从第二页开始
        cache_key = f'{base_cache_key}_page_{page_number}'
        cache.set(cache_key, sorted_remaining_results[i:i+5])



