from django.shortcuts import render

# Create your views here.
from .documents import *
from django.http import JsonResponse
import threading


def search_view(request):
    text = request.GET.get('text')
    list1 = []
    documents_list = [ScholarDocument1, ScholarDocument2, ScholarDocument3, ScholarDocument4, ScholarDocument5,
                      ScholarDocument6, ScholarDocument7, ScholarDocument8, ScholarDocument9, ScholarDocument10]

    def perform_search(doc):
        search = doc.search().sort('_doc')
        results = search.filter("match", abstract=text).to_queryset()
        list1.extend(list(results.values()))

    threads = []
    for d in documents_list:
        thread = threading.Thread(target=perform_search, args=(d,))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    return JsonResponse({
        'code': 200,
        'data': list1,
        'size': len(list1)
    })
