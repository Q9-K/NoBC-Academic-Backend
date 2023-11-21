from django.http import JsonResponse
from NoBC.commons import Commons


def response(msg, code=Commons.SUCCESS, data=None):
    return JsonResponse({
        'code': code,
        'msg': msg,
        'data': data
    })
