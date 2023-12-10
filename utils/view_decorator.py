from functools import wraps
from django.http import JsonResponse
from NoBC.status_code import *


def allowed_methods(methods):
    """
    装饰器，用于限制视图函数只能接受指定的HTTP请求方法。

    参数:
    - methods: 一个包含允许的HTTP请求方法的列表，如 ['GET', 'POST']。
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method not in methods:
                return JsonResponse({
                    'code': METHOD_ERROR,
                    'error': True,
                    'message': 'allowed method(s) are [{}]'.format(', '.join(methods)),
                    'data': {},
                })
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator
