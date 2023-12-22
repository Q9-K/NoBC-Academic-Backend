from datetime import datetime

from NoBC.status_code import *
from author.models import Author
from manager.models import Manager
from message.models import Certification, Complaint, Message
from user.models import User
from utils.Response import response
from utils.Token import generate_token
from utils.qos import get_file
from utils.view_decorator import allowed_methods, manager_login_required


# Create your views here.

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


@allowed_methods(['GET'])
@manager_login_required
def get_certifications_pending(request):
    """
    获取需要审核的认证
    :param request: token
    :return: [code, msg, data, error] data为需要审核的认证列表
    """
    certifications = Certification.objects.filter(status=Certification.PENDING)
    data = [certification.to_string() for certification in certifications]
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
    data = [certification.to_string() for certification in certifications]
    return response(SUCCESS, '获取所有的认证记录成功！', data=data)


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
            idcard_img_url = certification.idcard_img_url
            ret = get_file(idcard_img_url)
            if ret:
                data['idcard_img'] = ret
            else:
                return response(MYSQL_ERROR, '获取认证详情失败！', error=True)
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
    complaints = Complaint.objects.filter(status=Complaint.PENDING)
    data = [complaint.to_string() for complaint in complaints]
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
    data = [complaint.to_string() for complaint in complaints]
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
            elif status_code == '2':
                certification.status = Certification.REJECTED
                # 给该用户发消息
                title = '你的学者认证未通过'
                content = '你的学者认证未通过，原因：' + opinion
                create_message(title, content, certification.user)
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
                to_user = User.objects.get(scholar_identity=complaint.to_author)
                to_user.scholar_identity = None
                to_user.save()
                # 给被投诉的学者发消息
                title = '你的学者认证已被取消'
                content = '你的学者认证已被取消，原因：' + opinion
                create_message(title, content, to_user)
                # 给投诉者发消息
                title = '你的投诉已通过'
                content = '你的投诉已通过，原因：' + opinion
                create_message(title, content, complaint.user)
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
