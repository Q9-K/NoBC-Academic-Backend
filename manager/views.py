from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections

from NoBC.status_code import *
from config import ELAS_USER, ELAS_PASSWORD, ELAS_HOST
from manager.models import Manager
from message.models import Certification, Complaint, Message
from user.models import User
from utils.Response import response
from utils.Token import generate_token
from utils.qos import get_file
from utils.view_decorator import allowed_methods, manager_login_required

# Create your views here.

ES_NAME = 'author'
ES_CONN = connections.create_connection(hosts=[ELAS_HOST], http_auth=(ELAS_USER, ELAS_PASSWORD), timeout=20)


def login(request):
    """
    管理员登录
    :param request: name password
    :return: token
    """
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        name = request.POST.get('name')
        password = request.POST.get('password')
        try:
            manager = Manager.objects.get(name=name)
            if password != manager.password:
                return response(PARAMS_ERROR, '用户名或密码错误！', error=True)
            else:
                dic = {'name': name}
                token = generate_token(dic, 60 * 60 * 24)
                return response(SUCCESS, '登录成功！', data=token)
        except Manager.DoesNotExist:
            return response(PARAMS_ERROR, '用户名或密码错误！', error=True)


def get_message_data(dic: dict, user_avatar_key, author_id: str, default_author_avatar: str):
    # 加上用户和学者头像
    dic['user_avatar'] = get_file(user_avatar_key)
    search = Search(using=ES_CONN, index=ES_NAME).query('term', id=author_id)
    ret = search.execute().to_dict()['hits']['hits']
    if len(ret) == 0:
        dic['author_avatar'] = ''
        dic['author_name'] = ''
    else:
        dic['author_name'] = ret[0]['_source']['display_name']
        author_avatar_key = ret[0]['_source']['avatar']
        if author_avatar_key:
            dic['author_avatar'] = get_file(author_avatar_key)
        else:
            dic['author_avatar'] = default_author_avatar
    return dic


@allowed_methods(['GET'])
@manager_login_required
def get_certifications_pending(request):
    """
    获取需要审核的认证
    :param request: token
    :return: [code, msg, data, error] data为需要审核的认证列表
    """
    certifications = Certification.objects.filter(status=Certification.PENDING)
    data = []
    default_author_avatar = get_file('default_author.png')
    if default_author_avatar == '':
        return response(MYSQL_ERROR, '获取头像失败', error=True)
    for certification in certifications:
        dic = certification.to_string()
        user_avatar_key = certification.user.avatar_key
        author_id = certification.author.id
        certification_data = get_message_data(dic, user_avatar_key, author_id, default_author_avatar)
        if certification_data:
            data.append(certification_data)
        else:
            return response(MYSQL_ERROR, '获取需要审核的认证记录失败', error=True)
    return response(SUCCESS, '获取需要审核的认证记录成功！', data=data)


@allowed_methods(['GET'])
@manager_login_required
def get_certifications_all(request):
    """
    获取所有的认证
    :param request: token
    :return: [code, msg, data, error] data为所有的认证列表
    """
    certifications = Certification.objects.all()
    data = []
    default_author_avatar = get_file('default_author.png')
    if default_author_avatar == '':
        return response(MYSQL_ERROR, '获取头像失败', error=True)
    for certification in certifications:
        dic = certification.to_string()
        user_avatar_key = certification.user.avatar_key
        author_id = certification.author.id
        certification_data = get_message_data(dic, user_avatar_key, author_id, default_author_avatar)
        if certification_data:
            data.append(certification_data)
        else:
            return response(MYSQL_ERROR, '获取所有的认证记录失败', error=True)
    return response(SUCCESS, '获取所有的认证记录成功！', data=data)


def get_image_name(num: int) -> str:
    """
    获取图片名
    :param num: 图片序号
    :return: 图片名
    """
    if num == 1:
        return 'idcard_img_urlOne'
    elif num == 2:
        return 'idcard_img_urlTwo'
    elif num == 3:
        return 'idcard_img_urlThree'
    elif num == 4:
        return 'idcard_img_urlFour'
    else:
        return ''


@allowed_methods(['GET'])
@manager_login_required
def get_certification_detail(request):
    """
    获取认证详情
    :param request: token certification_id
    :return: [code, msg, data, error] data为认证详情
    """
    certification_id = request.GET.get('certification_id', None)
    if certification_id:
        try:
            certification = Certification.objects.get(id=certification_id)
            data = certification.to_string()
            data['author_name'] = get_author_name(certification.author_id)
            for i in range(1, 5):
                image_name = get_image_name(i)
                if image_name != '':
                    data[image_name] = get_file(data[image_name])
                else:
                    data[image_name] = ''
            return response(SUCCESS, '获取认证详情成功！', data=data)
        except Certification.DoesNotExist:
            return response(MYSQL_ERROR, '不存在此认证记录！', error=True)
    else:
        return response(PARAMS_ERROR, '字段不可为空！', error=True)


@allowed_methods(['GET'])
@manager_login_required
def get_complaints_pending(request):
    """
    获取需要审核的投诉
    :param request: token
    :return: [code, msg, data, error] data为需要审核的投诉列表
    """
    default_author_avatar = get_file('default_author.png')
    if default_author_avatar == '':
        return response(MYSQL_ERROR, '获取头像失败', error=True)
    complaints = Complaint.objects.filter(status=Complaint.PENDING)
    data = []
    for complaint in complaints:
        dic = complaint.to_string()
        author_id = complaint.to_author.id
        user_avatar_key = complaint.user.avatar_key
        get_message_data(dic, user_avatar_key, author_id, default_author_avatar)
        data.append(dic)
    return response(SUCCESS, '获取需要审核的投诉记录成功！', data=data)


@allowed_methods(['GET'])
@manager_login_required
def get_complaints_all(request):
    """
    获取需要审核的投诉
    :param request: token
    :return: [code, msg, data, error] data为需要审核的投诉列表
    """
    complaints = Complaint.objects.all()
    data = []
    default_author_avatar = get_file('default_author.png')
    if default_author_avatar == '':
        return response(MYSQL_ERROR, '获取头像失败', error=True)
    for complaint in complaints:
        dic = complaint.to_string()
        author_id = complaint.to_author.id
        user_avatar_key = complaint.user.avatar_key
        get_message_data(dic, user_avatar_key, author_id, default_author_avatar)
        data.append(dic)
    return response(SUCCESS, '获取全部的投诉记录成功！', data=data)


@allowed_methods(['POST'])
@manager_login_required
def check_certification(request):
    """
    审核认证
    :param request: token certification_id status opinion, status: 1 pass 2 reject
    :return: [code, msg, data, error]
    """
    certification_id = request.POST.get('certification_id', None)
    # 1 pass 2 reject
    status_code = request.POST.get('status', None)
    # 审核意见
    opinion = request.POST.get('opinion', '')
    if certification_id and status_code:
        try:
            certification = Certification.objects.get(id=certification_id, status=Certification.PENDING)
            if status_code == '1':
                certification.status = Certification.PASSED
                # 如果通过了,那么将对应用户的认证学者记录
                certification.user.scholar_identity = certification.author
                certification.user.save()
                # 给该用户发消息
                title = '你的学者认证已通过'
                content = '你的学者认证已通过，原因：' + opinion
                create_message(title, content, certification.user)
                send_message(certification.user.email, '你的学者认证已通过')
            elif status_code == '2':
                certification.status = Certification.REJECTED
                # 给该用户发消息
                title = '你的学者认证未通过'
                content = '你的学者认证未通过，原因：' + opinion
                create_message(title, content, certification.user)
                send_message(certification.user.email, '你的学者认证未通过')
            else:
                return response(PARAMS_ERROR, 'status错误！', error=True)
            certification.result_msg = opinion
            certification.save()
            return response(SUCCESS, '审核成功！')
        except Certification.DoesNotExist:
            return response(MYSQL_ERROR, '不存在此认证记录或已经审核过！', error=True)
    else:
        return response(PARAMS_ERROR, '字段不可为空！', error=True)


@allowed_methods(['POST'])
@manager_login_required
def check_complaint(request):
    """
    审核投诉
    :param request: token complaint_id status opinion, status: 1 pass 2 reject
    :return: [code, msg, data, error]
    """
    complaint_id = request.POST.get('complaint_id', None)
    # 1 pass 2 reject
    status_code = request.POST.get('status', None)
    # 审核意见
    opinion = request.POST.get('opinion', '')
    if complaint_id and status_code:
        try:
            complaint = Complaint.objects.get(id=complaint_id, status=Complaint.PENDING)
            if status_code == '1':
                complaint.status = Complaint.PASSED
                # 投诉通过,取消该学者的认证
                try:
                    to_user = User.objects.get(scholar_identity=complaint.to_author)
                    to_user.scholar_identity = None
                    to_user.save()
                # 没有认证这个学者的用户,直接成功
                except User.DoesNotExist:
                    complaint.save()
                    return response('审核成功')
                # 给被投诉的学者发消息
                title = '你的学者认证已被取消'
                content = '你的学者认证已被取消，原因：' + opinion
                create_message(title, content, to_user)
                send_message(to_user.email, '你的学者认证已被取消')
                # 给投诉者发消息
                title = '你的投诉已通过'
                content = '你的投诉已通过，原因：' + opinion
                create_message(title, content, complaint.user)
                send_message(complaint.user.email, '你的投诉已通过')
            elif status_code == '2':
                complaint.status = Complaint.REJECTED
                # 给投诉者发消息
                title = '你的投诉未通过'
                content = '你的投诉未通过，原因：' + opinion
                create_message(title, content, complaint.user)
            else:
                return response(PARAMS_ERROR, 'status错误！', error=True)
            complaint.result_msg = opinion
            complaint.save()
            return response(SUCCESS, '审核成功！')
        except Complaint.DoesNotExist:
            return response(MYSQL_ERROR, '不存在此投诉记录或已经审核过！', error=True)
    else:
        return response(PARAMS_ERROR, '字段不可为空！', error=True)


@allowed_methods(['GET'])
@manager_login_required
def get_complaint_detail(request):
    """
    获取投诉详情
    :param request: token complaint_id
    :return: [code, msg, data, error] data为投诉详情
    """
    complaint_id = request.GET.get('complaint_id', None)
    if complaint_id:
        try:
            complaint = Complaint.objects.get(id=complaint_id)
            data = complaint.to_string()
            data['author_name'] = get_author_name(complaint.to_author_id)
            return response(SUCCESS, '获取投诉详情成功！', data=data)
        except Complaint.DoesNotExist:
            return response(MYSQL_ERROR, '不存在此投诉记录！', error=True)
    else:
        return response(PARAMS_ERROR, '字段不可为空！', error=True)


def create_message(title, content, to_user):
    """
    创建消息
    :param title: 消息标题
    :param content: 消息内容
    :param to_user: 接收用户
    """
    message = Message(title=title, content=content, receiver=to_user, create_time=datetime.now())
    message.save()


def get_author_name(author_id):
    """
    获取学者姓名
    :param author_id: 学者id
    :return: 学者姓名
    """
    # es搜索
    search = Search(using=ES_CONN, index=ES_NAME).query('term', id=author_id)
    ret = search.execute().to_dict()['hits']['hits']
    if len(ret) == 0:
        return '未知'
    else:
        return ret[0]['_source']['display_name']


def get_user_by_email(email):
    try:
        user = User.objects.get(email=email)
        return user
    except User.DoesNotExist:
        return None


@allowed_methods(['GET'])
@manager_login_required
def get_user_info_by_email(request):
    """
    通过邮箱获取用户信息
    :param request: token, email
    :return: 用户信息
    """
    email = request.GET.get('user_email', None)
    if email:
        user = get_user_by_email(email)
        if email:
            return response('获取用户信息成功', data=user.to_string())
        else:
            return response(MYSQL_ERROR, '用户不存在', error=True)
    else:
        return response(PARAMS_ERROR, '字段不能为空', error=True)


@allowed_methods(['GET'])
@manager_login_required
def get_user_avatar_by_email(request):
    """
    获取用户头像
    :param request: token
    :return: [code, msg, data, error], 其中data为头像url
    """
    email = request.GET.get('user_email', None)
    if email:
        user = get_user_by_email(email)
        if user:
            if user.avatar_key != '':
                ret = get_file(user.avatar_key)
                if ret != '':
                    return response('获取用户头像成功', data=ret)
                else:
                    return response(MYSQL_ERROR, '获取用户头像失败', error=True)
            else:
                return response(MYSQL_ERROR, '获取用户头像失败', error=True)
        else:
            return response(MYSQL_ERROR, '用户不存在', error=True)
    else:
        return response(PARAMS_ERROR, '字段不能为空', error=True)


def send_message(user_email: str, message: str):
    """
    websocket 示例
    """
    # 截取数字
    user_email_prefix = user_email.split('@')[0]
    channel_layer = get_channel_layer()
    room_name = f'user_{user_email_prefix}'

    # 异步方式发送消息
    async_to_sync(channel_layer.group_send)(
        room_name,
        {
            'type': 'send_message',
            'message': message
        }
    )
    return response('发送成功', data=message)
