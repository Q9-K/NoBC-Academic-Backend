
# Create your views here.
from django.http import JsonResponse
from NoBC.commons import Commons
from .models import User


def register_view(request):
    if request.method != 'POST':
        return JsonResponse({
            'code': Commons.METHOD_ERROR,
            'msg': '请求方法错误'
        })
    else:
        name = request.POST.get('name')
        password = request.POST.get('password')
        print(request.POST)
        if name and password:
            User.objects.create(name=name, password=password)
            return JsonResponse({
                'code': Commons.SUCCESS,
                'msg': '注册成功123！'
            })
        else:
            return JsonResponse({
                'code': Commons.PARAMS_ERROR,
                'msg': '提交字段不允许有空子段！'
            })


def login_view(request):
    if request.method != 'POST':
        return JsonResponse({
            'code': Commons.METHOD_ERROR,
            'msg': '请求方法错误'
        })
    else:
        who = request.POST.get('id')
        password = request.POST.get('password')
        user = User.objects.get(who, password)


def search_view(request):
    from .documents import UserDocument
    text = request.GET.get('text')
    results = UserDocument.search().query("match", name=text)
    for hit in results:
        print(hit.name)
    return JsonResponse({
        'code': 200
    })
