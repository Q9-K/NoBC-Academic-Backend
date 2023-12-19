from manager.models import Manager
from utils.Response import response
from NoBC.status_code import *
from utils.Token import generate_token, get_value
from message.models import Certification, Complaint


# Create your views here.

def login_view(request):
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
        except Exception:
            return response(PARAMS_ERROR, '用户名或密码错误！', error=True)


def get_certifications(request):
    """
    获取需要审核的认证
    :param request: token
    :return: [code, msg, data, error] data为需要审核的认证列表
    """
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token', None)
        value = get_value(token)
        if value:
            name = value['name']
            try:
                Manager.objects.get(name=name)
                certifications = Certification.objects.all()
                data = [certification.to_string() for certification in certifications]
                return response(SUCCESS, '获取需要审核的认证记录成功！', data=data)
            except Exception:
                return response(MYSQL_ERROR, '不存在此管理员！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


def get_complaints(request):
    """
    获取需要审核的投诉
    :param request: token
    :return: [code, msg, data, error] data为需要审核的投诉列表
    """
    if request.method != 'GET':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.GET.get('token', None)
        value = get_value(token)
        if value:
            name = value['name']
            try:
                Manager.objects.get(name=name)
                complaints = Complaint.objects.all()
                data = [complaint.to_string() for complaint in complaints]
                return response(SUCCESS, '获取需要审核的投诉记录成功！', data=data)
            except Exception:
                return response(MYSQL_ERROR, '不存在此管理员！', error=True)
        else:
            return response(PARAMS_ERROR, 'token错误！', error=True)


def check_certification(request):
    """
    审核认证
    :param request: token certification_id status opinion, status: 1 pass 2 reject
    :return: [code, msg, data, error]
    """
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.POST.get('token', None)
        certification_id = request.POST.get('certification_id', None)
        # 1 pass 2 reject
        status_code = request.POST.get('status', None)
        # 审核意见
        opinion = request.POST.get('opinion', '')
        if token and certification_id and status_code:
            value = get_value(token)
            if value:
                name = value['name']
                try:
                    Manager.objects.get(name=name)
                    try:
                        certification = Certification.objects.get(id=certification_id)
                        if status_code == '1':
                            certification.status = Certification.PASSED
                        elif status_code == '2':
                            certification.status = Certification.REJECTED
                        else:
                            return response(PARAMS_ERROR, 'status错误！')
                        certification.result_msg = opinion
                    except Exception:
                        return response(PARAMS_ERROR, '不存在此认证记录！')
                except Exception:
                    return response(PARAMS_ERROR, '不存在此管理员！')
            else:
                return response(PARAMS_ERROR, 'token错误！')
        else:
            return response(PARAMS_ERROR, '字段不可为空！')


# 审核投诉
def check_complaint(request):
    """
    审核投诉
    :param request: token complaint_id status opinion, status: 1 pass 2 reject
    :return: [code, msg, data, error]
    """
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        token = request.POST.get('token', None)
        complaint_id = request.POST.get('complaint_id', None)
        # 1 pass 2 reject
        status_code = request.POST.get('status', None)
        # 审核意见
        opinion = request.POST.get('opinion', '')
        if token and complaint_id and status_code:
            value = get_value(token)
            if value:
                name = value['name']
                try:
                    Manager.objects.get(name=name)
                    try:
                        complaint = Complaint.objects.get(id=complaint_id)
                        if status_code == '1':
                            complaint.status = Complaint.PASSED
                        elif status_code == '2':
                            complaint.status = Complaint.REJECTED
                        else:
                            return response(PARAMS_ERROR, 'status错误！', error=True)
                        complaint.result_msg = opinion
                    except Exception:
                        return response(MYSQL_ERROR, '不存在此投诉记录！', error=True)
                except Exception:
                    return response(MYSQL_ERROR, '不存在此管理员！', error=True)
            else:
                return response(PARAMS_ERROR, 'token错误！', error=True)
        else:
            return response(PARAMS_ERROR, '字段不可为空！', error=True)
