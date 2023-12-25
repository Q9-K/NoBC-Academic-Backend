import os
import random
import re
from datetime import datetime

from django.core.mail import send_mail
from elasticsearch_dsl import connections, Search

from NoBC.status_code import *
from author.models import Author
from concept.models import Concept
from config import BUAA_MAIL_USER, ELAS_HOST, ELAS_USER, ELAS_PASSWORD
from message.models import Certification, Complaint, Message
from utils.Md5 import create_md5, create_salt
from utils.Response import response
from utils.Token import generate_token
from utils.generate_avatar import render_identicon
from utils.qos import upload_file, get_file, delete_file
from utils.view_decorator import login_required, allowed_methods
from work.models import Work
from work.views import get_citation
from .models import User, History, Favorite

ES_CONN = connections.get_connection()


def init_user_avatar(user: User) -> str:
    """
    初始化用户头像
    :param user: 用户对象
    """
    email = user.email
    key = email + '_avatar.png'
    render_identicon(key)
    upload_file(key, 'tempFile/' + key)
    user.avatar_key = key
    user.save()
    # 删除本地存储的文件
    path_file = 'tempFile/' + key
    os.remove(path_file)
    return key


def save_file(file):
    """
    保存文件
    :param file: 文件对象
    :return: 文件名
    """
    # 获取文件名
    file_name = file.name
    # 获取文件后缀名
    file_suffix = file_name.split('.')[-1]
    # 生成文件名
    file_name = str(random.randint(100000, 999999)) + '.' + file_suffix
    # 保存文件
    file_path = 'tempFile/' + file_name
    with open(file_path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
    return file_path


@allowed_methods(['POST'])
@login_required
def upload_user_avatar(request):
    avatar = request.FILES.get('avatar', None)
    if avatar:
        file_path = save_file(avatar)
        user = request.user
        user: User
        # 删除原有头像
        delete_file(user.avatar_key)
        # 上传新头像
        ret = upload_file(user.email + '_avatar.png', file_path)
        if ret:
            # 删除本地存储的文件
            os.remove(file_path)
            return response(SUCCESS, '上传头像成功！')
        else:
            os.remove(file_path)
            return response(FILE_ERROR, '上传头像失败！', error=True)
    else:
        return response(PARAMS_ERROR, '头像不能为空')


@allowed_methods(['GET'])
@login_required
def get_user_avatar(request):
    """
    获取用户头像
    :param request: token
    :return: [code, msg, data, error], 其中data为头像url
    """
    user = request.user
    user: User
    avatar_key = user.avatar_key
    if avatar_key:
        avatar_url = get_file(avatar_key)
        return response(SUCCESS, '获取用户头像成功！', data=avatar_url)
    else:
        return response(SUCCESS, '用户头像不存在！')


@allowed_methods(['POST'])
def test(request):
    user = User.objects.get(email='326855092@qq.com')
    key = init_user_avatar(user)
    user.avatar_key = key
    user.save()
    return response(data=None)


def send_email(email) -> int:
    """
    发送邮件
    :param email: 对方邮箱
    :return: 验证码
    """
    # 生成随机六位数验证码
    code = random.randint(100000, 999999)
    send_mail(
        "NoBC注册",
        f"欢迎注册NoBC平台,这是你的验证码:{code}",
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
            re_str = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
            if not re.match(re_str, email):
                return response(PARAMS_ERROR, '邮箱格式错误！', error=True)
            if User.objects.filter(email=email, is_active=True):
                return response(PARAMS_ERROR, '邮箱已注册过！', error=True)
            if password != password_repeat:
                return response(PARAMS_ERROR, '两次密码不一致！', error=True)
            # 发送邮件
            try:
                code = send_email(email)
            except Exception:
                return response(PARAMS_ERROR, '发送邮件失败！', error=True)
            salt = create_salt()
            password_encode = create_md5(password, salt)
            # 创建用户, is_active=False, 未激活, 激活后才能登录,update_or_create,如果存在则更新,不存在则创建
            default_fields = {'name': name, 'password': password_encode, 'salt': salt}
            User.objects.update_or_create(defaults=default_fields, email=email)
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
                    # 注册成功后给用户生成默认头像
                    init_user_avatar(user)
                    # 注册成功后直接登录,返回token
                    dic = {'email': user.email, 'name': user.name}
                    token = generate_token(dic, 60 * 60 * 24)
                    return response(SUCCESS, '注册成功', data=token)
                else:
                    return response(PARAMS_ERROR, '验证码错误', error=True)
            except User.DoesNotExist:
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
                    return response(PARAMS_ERROR, '邮箱或密码错误！', error=True)
                else:
                    dic = {'email': user.email, 'name': user.name}
                    token = generate_token(dic, 60 * 60 * 24)
                    data = dict()
                    data['token'] = token
                    data['name'] = user.name
                    return response(SUCCESS, '登录成功！', data=data)
            except User.DoesNotExist:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, '邮箱和密码不可为空', error=True)


@allowed_methods(['GET'])
@login_required
def get_histories(request):
    """
    获取用户浏览记录
    :param request: token
    :return: [code, msg, data, error], 其中data为浏览记录列表
    """
    user = request.user
    user: User
    histories = user.history_set.all()
    histories_info = [{'work_id': history.work.id, 'date_time': history.date_time} for history in histories]
    # 遍历id,查找论文拼接信息
    data = []
    for history in histories_info:
        data.append(get_work_info(history, user))
    return response(SUCCESS, '获取用户浏览记录成功！', data=data)


def get_work_info(work: dict, user: User = None):
    """
    获取论文信息根据论文id查找论文并拼接信息
    """
    search = Search(using=ES_CONN, index='work').query('term', id=work['work_id'])
    ret = search.execute().to_dict()['hits']['hits']
    if len(ret) == 0:
        return None
    ret = ret[0]['_source']
    # 拼接论文信息,需要title, author_name, citation
    work_data = dict()
    work_data['title'] = ret['title']
    work_data['id'] = ret['id']
    work_data['citation'] = get_citation(ret)
    work_data['authors'] = [{'name': authorship['author']['display_name'],
                             'id': authorship['author']['id'],
                             } for authorship in ret['authorships']]
    # 如果传入了user,则判断是否收藏;否则默认为收藏
    if user:
        work_data['collected'] = user.favorites.filter(id=work['work_id']).exists()
        work_data['collectionTime'] = None
    else:
        work_data['collected'] = True
        work_data['collectionTime'] = work['collection_time']
    return work_data


@allowed_methods(['GET'])
@login_required
def get_favorites(request):
    """
    获取用户收藏记录
    :param request: token
    :return: [code, msg, data, error], 其中data为收藏记录列表
    """
    user = request.user
    user: User
    favorites = user.favorite_set.all()
    favorites_info = [{'work_id': favorite.work.id, 'collection_time': favorite.collection_time}
                      for favorite in favorites]
    # 遍历id,查找论文拼接信息
    data = []
    for favorite in favorites_info:
        data.append(get_work_info(favorite))
    return response(SUCCESS, '获取用户收藏记录成功！', data=data)


@allowed_methods(['GET'])
@login_required
def get_focus_concepts(request):
    """
    获取用户关注的领域
    :param request: token
    :return: [code, msg, data, error], 其中data为领域列表
    """
    user = request.user
    user: User
    concepts = user.concept_focus.all()
    data = [concept.to_string() for concept in concepts]
    return response(SUCCESS, '获取用户关注的领域成功！', data=data)


@allowed_methods(['GET'])
@login_required
def get_messages(request):
    """
    获取用户站内信
    :param request: token
    :return: [code, msg, data, error], 其中data为站内信列表
    """
    user = request.user
    user: User
    messages = user.msg.all()
    data = [message.to_string() for message in messages]
    return response(SUCCESS, '获取用户站内信成功！', data=data)


def get_author_info(author_id: str, user: User = None):
    search = Search(using=ES_CONN, index='author').query('term', id=author_id)
    ret = search.execute().to_dict()['hits']['hits']
    if len(ret) == 0:
        return None
    ret = ret[0]['_source']
    # 拼接学者信息,需要name, work_count, h_index, followed
    author_data = dict()
    author_data['id'] = ret['id']
    author_data['name'] = ret['display_name']
    author_data['papers'] = ret['works_count']
    author_data['H_index'] = ret['summary_stats']['h_index']
    # 头像为空则用默认的
    if ret['avatar']:
        author_data['avatar'] = get_file(ret['avatar'])
    else:
        author_data['avatar'] = get_file('default_author.png')
    author_data['englishAffiliation'] = None
    # 如果传入了user,则判断是否关注;否则默认为关注
    if user:
        author_data['followed'] = user.follows.filter(id=author_id).exists()
    else:
        author_data['followed'] = True
    return author_data


@allowed_methods(['GET'])
@login_required
def get_follows(request):
    """
    获取关注的学者
    :param request: token
    :return: [code, msg, data, error], 其中data为学者列表
    """
    user = request.user
    user: User
    authors = user.follows.all()
    authors_id = [author.to_string()['id'] for author in authors]
    # 遍历id,查找学者拼接信息
    data = []
    for author_id in authors_id:
        data.append(get_author_info(author_id))
    return response(SUCCESS, '获取用户关注的学者成功！', data=data)


@allowed_methods(['POST'])
@login_required
def follow_scholar(request):
    """
    关注学者
    :param request: scholar_id, token
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    scholar_id = request.POST.get('scholar_id', None)
    if not scholar_id:
        return response(PARAMS_ERROR, '缺少学者id！', error=True)
    try:
        scholar = Author.objects.get(id=scholar_id)
    except Author.DoesNotExist:
        # 不存在则创建
        scholar = Author.objects.create(id=scholar_id)
    if user.follows.filter(id=scholar_id).exists():
        return response(PARAMS_ERROR, '已关注该学者！', error=True)
    user.follows.add(scholar)
    return response(SUCCESS, '关注学者成功！')


@allowed_methods(['POST'])
@login_required
def unfollow_scholar(request):
    """
    取消关注学者
    :param request: scholar_id, token
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    scholar_id = request.POST.get('scholar_id', None)
    if not scholar_id:
        return response(PARAMS_ERROR, '缺少学者id！', error=True)
    try:
        scholar = user.follows.get(id=scholar_id)
        user.follows.remove(scholar)
        return response(SUCCESS, '取消关注学者成功！')
    except Author.DoesNotExist:
        return response(MYSQL_ERROR, '未关注该学者！', error=True)


@allowed_methods(['POST'])
@login_required
def add_focus_concept(request):
    """
    关注领域
    :param request: concept_id, token
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    concept_id = request.POST.get('concept_id', None)
    if not concept_id:
        return response(PARAMS_ERROR, '缺少领域id！', error=True)
    try:
        concept = Concept.objects.get(id=concept_id)
    except Concept.DoesNotExist:
        # 领域不存在,创建领域
        concept = Concept.objects.create(id=concept_id)
        concept.save()
    if user.concept_focus.filter(id=concept_id).exists():
        return response(PARAMS_ERROR, '已关注该领域！', error=True)
    user.concept_focus.add(concept)
    return response(SUCCESS, '关注领域成功！')


@allowed_methods(['POST'])
@login_required
def remove_focus_concept(request):
    """
    取消关注领域
    :param request: concept_id, token
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    concept_id = request.POST.get('concept_id', None)
    if not concept_id:
        return response(PARAMS_ERROR, '缺少领域id！', error=True)
    try:
        concept = user.concept_focus.get(id=concept_id)
        user.concept_focus.remove(concept)
        return response(SUCCESS, '取消关注领域成功！')
    except Concept.DoesNotExist:
        return response(MYSQL_ERROR, '未关注该领域！', error=True)


@allowed_methods(['GET'])
@login_required
def get_user_info(request):
    """
    获取用户信息
    :param request: token
    :return: [code, msg, data, error], 其中data为用户信息
    """
    user = request.user
    user: User
    data = user.to_string()
    return response(SUCCESS, '获取用户信息成功！', data=data)


@allowed_methods(['POST'])
@login_required
def record_history(request):
    """
    记录浏览记录
    :param request: token, paper_id
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    work_id = request.POST.get('work_id', None)
    if not work_id:
        return response(PARAMS_ERROR, '缺少论文id！', error=True)
    # 论文不存在,创建论文
    work = Work.objects.filter(id=work_id)
    if not work:
        work = Work.objects.create(id=work_id)
        work.save()
    work = Work.objects.get(id=work_id)
    # 通过中间表记录浏览记录
    History.objects.create(user=user, work=work, date_time=datetime.now())
    return response(SUCCESS, '记录浏览记录成功！')


@allowed_methods(['POST'])
@login_required
def add_favorite(request):
    """
    添加收藏
    :param request: token, paper_id
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    work_id = request.POST.get('work_id', None)
    if not work_id:
        return response(PARAMS_ERROR, '缺少论文id！', error=True)
    # 论文不存在,创建论文
    if not Work.objects.filter(id=work_id):
        work = Work.objects.create(id=work_id)
        work.save()
    work = Work.objects.get(id=work_id)
    if user.favorites.filter(id=work_id).exists():
        return response(PARAMS_ERROR, '已收藏该论文！', error=True)
    Favorite.objects.create(user=user, work=work, collection_time=datetime.now())
    return response(SUCCESS, '添加收藏成功！')


@allowed_methods(['POST'])
@login_required
def remove_favorite(request):
    """
    取消收藏
    :param request: token, paper_id
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    work_id = request.POST.get('work_id', None)
    if not work_id:
        return response(PARAMS_ERROR, '缺少论文id！', error=True)
    if not user.favorites.filter(id=work_id).exists():
        return response(PARAMS_ERROR, '未收藏该论文！', error=True)
    user.favorites.remove(work_id)
    return response(SUCCESS, '取消收藏成功！')


@allowed_methods(['POST'])
@login_required
def clear_histories(request):
    """
    清空浏览记录
    :param request: token
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    user.histories.clear()
    return response(SUCCESS, '清空浏览记录成功！')


@allowed_methods(['POST'])
@login_required
def change_user_info(request):
    name = request.POST.get('name', '')
    real_name = request.POST.get('real_name', '')
    position = request.POST.get('position', '')
    organization = request.POST.get('organization', '')
    subject = request.POST.get('subject', '')
    gender = request.POST.get('gender', '')
    # 进行更新
    user = request.user
    user: User
    user.name = name
    user.real_name = real_name
    user.position = position
    user.organization = organization
    user.subject = subject
    user.gender = gender
    user.save()
    return response(SUCCESS, '修改用户信息成功！')


@allowed_methods(['POST'])
@login_required
def de_authentication(request):
    """
    解除学者人这个
    :param request:
    :return:
    """
    user = request.user
    user: User
    user.scholar_identity = None
    user.save()
    return response(SUCCESS, '解除认证成功！')


@allowed_methods(['GET'])
@login_required
def check_concept_focus(request):
    """
    检查用户是否关注领域
    :param request: token, concept_id
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    concept_id = request.GET.get('concept_id', None)
    if not concept_id:
        return response(PARAMS_ERROR, '缺少领域id！', error=True)
    data = dict()
    data['focus'] = user.concept_focus.filter(id=concept_id).exists()
    return response(SUCCESS, '检查用户是否关注领域成功！', data=data)


@allowed_methods(['GET'])
@login_required
def check_author_follow(request):
    """
    检查用户是否关注学者
    :param request: token, author_id
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    author_id = request.GET.get('author_id', None)
    if not author_id:
        return response(PARAMS_ERROR, '缺少学者id！', error=True)
    data = dict()
    data['followed'] = user.follows.filter(id=author_id).exists()
    return response(SUCCESS, '检查用户是否关注学者成功！', data=data)


@allowed_methods(['POST'])
@login_required
def relieve_certification(request):
    """
    解除认证
    :param request: token
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    if not user.scholar_identity:
        return response(PARAMS_ERROR, '用户未认证！', error=True)
    user.scholar_identity = None
    user.save()
    return response(SUCCESS, '解除认证成功！')


@allowed_methods(['POST'])
@login_required
def apply_for_certification(request):
    """
    申请认证
    :param request: token, author_id
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    # 如果已经认证,要先解除认证
    if user.scholar_identity:
        return response(PARAMS_ERROR, '用户已认证！', error=True)
    author_id = request.POST.get('author_id', None)
    idcard_img_list = request.FILES.getlist('idcard_img', None)
    remark = request.POST.get('remark', None)
    if author_id and idcard_img_list and remark:
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            # 不存在则创建
            author = Author.objects.create(id=author_id)
        # 如果学者已经被认证过,返回错误
        if User.objects.filter(is_active=True, scholar_identity=author).exists():
            return response(MYSQL_ERROR, '该学者已经被认证过', error=True)
        # 先把文件存储到本地
        dic = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four'}
        keys = ['' for _ in range(4)]
        num = 1
        for idcard_img in idcard_img_list:
            file_path = save_file(idcard_img)
            # 使用七牛云对象存储上传图片
            key = user.email + '_idcard_img' + dic[num] + '.png'
            keys[num - 1] = key
            ret = upload_file(key, file_path)
            if ret:
                # 删除本地存储的文件
                os.remove(file_path)
            else:
                os.remove(file_path)
                return response(FILE_ERROR, '上传身份证失败！', error=True)
            num += 1
        # 创建认证消息
        certification = Certification.objects.create(user=user, author=author, content=remark,
                                                     idcard_img_urlOne=keys[0],
                                                     idcard_img_urlTwo=keys[1],
                                                     idcard_img_urlThree=keys[2],
                                                     idcard_img_urlFour=keys[3])
        certification.save()
        return response(SUCCESS, '申请认证成功！')
    else:
        return response(PARAMS_ERROR, '字段不可为空', error=True)


@allowed_methods(['GET'])
@login_required
def get_certification_status(request):
    """
    获取认证状态
    :param request: token
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    if not user.scholar_identity:
        return response(SUCCESS, '用户未认证！', data={'status': '未认证', 'scholar_id': None})
    else:
        return response(SUCCESS, '获取认证状态成功！', data={'status': '已认证', 'scholar_id': user.scholar_identity.id})


@allowed_methods(['POST'])
@login_required
def apply_for_complaint(request):
    """
    申请投诉
    :param request: token, author_id
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    author_id = request.POST.get('author_id', None)
    complaint_content = request.POST.get('complaint_content', None)
    if author_id and complaint_content:
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            # 不存在则创建
            author = Author.objects.create(id=author_id)
        if not User.objects.filter(scholar_identity=author).exists():
            return response(PARAMS_ERROR, '学者未认证！', error=True)
        # 创建投诉消息
        complaint = Complaint.objects.create(user=user, to_author=author, complaint_content=complaint_content)
        complaint.save()
        return response(SUCCESS, '申请投诉成功！')
    else:
        return response(PARAMS_ERROR, '字段不可为空', error=True)


@allowed_methods(['GET'])
@login_required
def get_messages_all(request):
    """
    获取全部站内信
    :param request: token
    :return: [code, msg, data, error]
    """
    user = request.user
    user: User
    messages = user.msg.all()
    data = [message.to_string() for message in messages]
    return response(SUCCESS, '获取全部站内信成功！', data=data)


def check_author_authentication(request):
    """
    查看学者是否已经认证过
    :param request: author_id
    :return: 认证过为True,否则False
    """
    author_id = request.GET.get('author_id', None)
    if author_id:
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            author = Author.objects.create(id=author_id)
            author.save()
        if User.objects.filter(is_active=True, scholar_identity=author).exists():
            data = True
        else:
            data = False
        return response(SUCCESS, '获取学者认证状态成功', data=data)
    else:
        return response(PARAMS_ERROR, '字段不能为空', error=True)


@allowed_methods(['POST'])
@login_required
def read_message(request):
    message_id = request.POST.get('message_id', None)
    if message_id:
        # 将消息改为已读
        try:
            message = Message.objects.get(id=message_id, status=Message.UNREAD)
            message.status = Message.READ
            message.save()
            return response(SUCCESS, '消息已读')
        except Message.DoesNotExist:
            return response(MYSQL_ERROR, '消息已读或不存在', error=True)
    else:
        return response(PARAMS_ERROR, '字段不能为空', error=True)
