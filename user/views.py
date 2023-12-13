import random

from django.core.mail import send_mail
from NoBC.status_code import *
from author.models import Author
from config import BUAA_MAIL_USER
from utils.Md5 import create_md5, create_salt
from utils.Response import response
from utils.Token import generate_token
from utils.Token import get_value
from .models import User


def send_email(email) -> int:
    """
    发送邮件
    :param email: 对方邮箱
    :return: 验证码
    """
    # 生成随机六位数验证码
    code = random.randint(100000, 999999)
    send_mail(
        "Subject",
        "欢迎注册NoBC平台,这是你的验证码:",
        BUAA_MAIL_USER,
        [email],
    )
    return code


def register_view(request):
    """
    注册
    :param request: email, name, password, password_repeat
    :return: [code, msg, data] 其中data中有验证码
    """
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        password_repeat = request.POST.get('password_repeat', None)
        if name and password and password_repeat and email:
            if User.objects.filter(email=email, is_active=True):
                return response(PARAMS_ERROR, '邮箱已注册过！', error=True)
            if password != password_repeat:
                return response(PARAMS_ERROR, '两次密码不一致！', error=True)
            # 发送邮件
            code = send_email(email)
            salt = create_salt()
            password_encode = create_md5(password, salt)
            # 创建用户, is_active=False, 未激活, 激活后才能登录,update_or_create,如果存在则更新,不存在则创建
            User.objects.update_or_create(name=name, password=password_encode, salt=salt, email=email)
            return response(SUCCESS, '请注意查收邮件！', data=code)
        else:
            return response(PARAMS_ERROR, '提交字段名不可为空！', error=True)


def active_user(request):
    """
    激活用户
    :param request: correct_code(验证码), get_code(用户输入验证码), email
    :return: [code, msg, data]
    """
    if request.method != "POST":
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        correct_code = request.POST.get('correct_code', None)
        get_code = request.POST.get('get_code', None)
        email = request.POST.get('email', None)
        if email and get_code and correct_code:
            try:
                user = User.objects.get(email=email, is_active=False)
                if get_code == correct_code:
                    user.activate()
                    return response(SUCCESS, '注册成功')
                else:
                    return response(PARAMS_ERROR, '验证码错误', error=True)
            except Exception:
                return response(MYSQL_ERROR, '该用户已经注册过', error=True)
        else:
            return response(PARAMS_ERROR, '提交字段名不可为空！', error=True)


def login_view(request):
    """
    登录
    :param request: email, password
    :return: [code, msg, data], 其中data为token(若登录成功,否则为None)
    """
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        email = request.POST.get('email', None)
        password = request.POST.get('password')
        if email and password:
            try:
                user = User.objects.get(email=email, is_active=True)
                salt = user.salt
                password_encode = create_md5(password, salt)
                if password_encode != user.password:
                    return response(PARAMS_ERROR, '用户名或密码错误！', error=True)
                else:
                    dic = {'email': email, 'name': user.name}
                    token = generate_token(dic, 60 * 60 * 24)
                    return response(SUCCESS, '登录成功！', data=token)
            except Exception:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, '用户名或密码错误！', error=True)


def get_histories(request):
    """
    获取用户浏览记录
    :param request: token
    :return: [code, msg, data, error], 其中data为浏览记录列表
    """
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token', None)
        value = get_value(token)
        if value:
            email = value['email']
            try:
                user = User.objects.get(email=email, is_active=True)
                histories = user.histories.all()
                data = [history.to_string() for history in histories]
                return response(SUCCESS, '获取用户浏览记录成功！', data=data)
            except Exception:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


def get_favorites(request):
    """
    获取用户收藏记录
    :param request: token
    :return: [code, msg, data, error], 其中data为收藏记录列表
    """
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token', None)
        value = get_value(token)
        if value:
            email = value['email']
            try:
                user = User.objects.get(email=email, is_active=True)
                favorites = user.favorites.all()
                data = [favorite.to_string() for favorite in favorites]
                return response(SUCCESS, '获取用户收藏记录成功！', data=data)
            except Exception:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


def get_concept_focus(request):
    """
    获取用户关注的领域
    :param request: token
    :return: [code, msg, data, error], 其中data为领域列表
    """
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token')
        value = get_value(token)
        if value:
            email = value['email']
            try:
                user = User.objects.get(email=email, is_active=True)
                concepts = user.concept_focus.all()
                data = [concept.to_string() for concept in concepts]
                return response(SUCCESS, '获取用户关注的领域成功！', data=data)
            except Exception:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


def get_messages(request):
    """
    获取用户站内信
    :param request: token
    :return: [code, msg, data, error], 其中data为站内信列表
    """
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token')
        value = get_value(token)
        if value:
            email = value['email']
            try:
                user = User.objects.get(email=email, is_active=True)
                messages = user.msg.all()
                data = [message.to_string() for message in messages]
                return response(SUCCESS, '获取用户站内信成功！', data=data)
            except Exception:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


def get_scholar_focus(request):
    """
    获取关注的学者
    :param request: token
    :return: [code, msg, data, error], 其中data为学者列表
    """
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token')
        value = get_value(token)
        if value:
            email = value['email']
            try:
                user = User.objects.get(email=email, is_active=True)
                scholars = user.follows.all()
                data = [scholar.to_string() for scholar in scholars]
                return response(SUCCESS, '获取用户关注的学者成功！', data=data)
            except Exception:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


def follow_scholar(request):
    """
    关注学者
    :param request: scholar_id, token
    :return: [code, msg, data, error]
    """
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token')
        value = get_value(token)
        if value:
            email = value['email']
            try:
                user = User.objects.get(email=email, is_active=True)
                scholar_id = request.POST.get('scholar_id', None)
                if not scholar_id:
                    return response(PARAMS_ERROR, '缺少学者id！', error=True)
                try:
                    scholar = Author.objects.get(id=scholar_id)
                    user.follows.add(scholar)
                    return response(SUCCESS, '关注学者成功！')
                except Exception:
                    return response(MYSQL_ERROR, '学者不存在！', error=True)
            except Exception:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)
