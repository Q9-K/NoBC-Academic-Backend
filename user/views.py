from author.models import Author
from message.models import Message
from utils.Md5 import create_md5, create_salt
from utils.Response import response
from utils.Token import generate_token
from utils.Token import get_value
from .models import User
from NoBC.status_code import *


def register_view(request):
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        name = request.POST.get('name', None)
        password = request.POST.get('password', None)
        password_repeat = request.POST.get('password_repeat', None)
        if name and password and password_repeat:
            if User.objects.filter(name=name):
                return response(PARAMS_ERROR, '用户名已存在！', error=True)
            if password != password_repeat:
                return response(PARAMS_ERROR, '两次密码不一致！', error=True)
            salt = create_salt()
            password_encode = create_md5(password, salt)
            User.objects.create(name=name, password=password_encode, salt=salt)
            return response(SUCCESS, '注册成功！')
        else:
            return response(PARAMS_ERROR, '提交字段名不可为空！', error=True)


def login_view(request):
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        name = request.POST.get('name')
        password = request.POST.get('password')
        user = User.objects.get(name=name)
        if user:
            salt = user.salt
            password_encode = create_md5(password, salt)
            if password_encode != user.password:
                return response(PARAMS_ERROR, '用户名或密码错误！', error=True)
            else:
                dic = {'name': name}
                token = generate_token(dic, 60 * 60 * 24)
                return response(SUCCESS, '登录成功！', data=token)
        else:
            return response(PARAMS_ERROR, '用户名或密码错误！', error=True)


# 获取用户浏览记录
def get_histories(request):
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token')
        value = get_value(token)
        if value:
            name = value['name']
            try:
                user = User.objects.get(name=name)
                histories = user.histories.all()
                data = []
                for history in histories:
                    data.append(history.to_string())
                return response(SUCCESS, '获取用户浏览记录成功！', data=data)
            except Exception as e:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


# 获取用户收藏记录
def get_favorites(request):
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token')
        value = get_value(token)
        if value:
            name = value['name']
            try:
                user = User.objects.get(name=name)
                favorites = user.favorites.all()
                data = []
                for favorite in favorites:
                    data.append(favorite.to_string())
                return response(SUCCESS, '获取用户收藏成功！', data=data)
            except Exception as e:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


# 获取用户关注的领域
def get_concept_focus(request):
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token')
        value = get_value(token)
        if value:
            name = value['name']
            try:
                user = User.objects.get(name=name)
                concepts = user.concept_focus.all()
                data = []
                for concept in concepts:
                    data.append(concept.to_string())
                return response(SUCCESS, '获取用户关注领域成功！', data=data)
            except Exception as e:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


# 获取用户站内信
def get_messages(request):
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token')
        value = get_value(token)
        if value:
            name = value['name']
            try:
                user = User.objects.get(name=name)
                messages = Message.objects.filter(receiver=user)
                data = []
                for message in messages:
                    data.append(message.to_string())
                return response(SUCCESS, '获取用户站内信成功！', data=data)
            except Exception as e:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


# 获取关注的学者
def get_scholar_focus(request):
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token')
        value = get_value(token)
        if value:
            name = value['name']
            try:
                user = User.objects.get(name=name)
                scholar = user.scholar_identity
                if scholar:
                    data = scholar.to_string()
                else:
                    data = None
                return response(SUCCESS, '获取关注的学者成功！', data=data)
            except Exception as e:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


# 关注学者
def follow_scholar(request):
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token')
        value = get_value(token)
        if value:
            name = value['name']
            try:
                user = User.objects.get(name=name)
                scholar_id = request.POST.get('scholar_id', None)
                if scholar_id:
                    try:
                        scholar = Author.objects.get(id=scholar_id)
                    except Exception as e:
                        # 不存在这个学者则创建
                        scholar = Author.objects.create(id=scholar_id)
                        scholar.save()
                    user.follows.add(scholar)
                    return response(SUCCESS, '关注学者成功')
                else:
                    return response(PARAMS_ERROR, '学者id不能为空', error=True)
            except Exception as e:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)
