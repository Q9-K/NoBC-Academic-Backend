from manager.models import Manager
from utils.Response import response
from NoBC.commons import Commons
from utils.Token import generate_token, get_value
from message.models import Certification, Complaint

# Create your views here.

# 管理员登录
def login_view(request):
    if request.method != 'POST':
        return response(Commons.METHOD_ERROR, '请求方法错误')
    else:
        name = request.POST.get('name')
        password = request.POST.get('password')
        try:
            manager = Manager.objects.get(name=name)
            if password != manager.password:
                return response(Commons.PARAMS_ERROR, '用户名或密码错误！')
            else:
                dic = {'name': name}
                token = generate_token(dic, 60 * 60 * 24)
                return response(Commons.SUCCESS, '登录成功！', data=token)
        except Exception as e:
            return response(Commons.PARAMS_ERROR, '用户名或密码错误！')


# 获取需要审核的认证
def get_certifications(request):
    if request.method != 'GET':
        return response(Commons.METHOD_ERROR, '请求方法错误')
    else:
        token = request.GET.get('token', None)
        value = get_value(token)
        if value:
            name = value['name']
            try:
                manager = Manager.objects.get(name=name)
                certifications = Certification.objects.all()
                data = []
                for certification in certifications:
                    data.append(certification.to_string())
                return response(Commons.SUCCESS, '获取需要审核的认证记录成功！', data=data)
            except Exception as e:
                return response(Commons.PARAMS_ERROR, '不存在此管理员！')
        else:
            return response(Commons.PARAMS_ERROR, 'token错误！')


# 获取需要审核的投诉
def get_complaints(request):
    if request.method != 'GET':
        return response(Commons.METHOD_ERROR, '请求方法错误')
    else:
        token = request.GET.get('token', None)
        value = get_value(token)
        if value:
            name = value['name']
            try:
                manager = Manager.objects.get(name=name)
                complaints = Complaint.objects.all()
                data = []
                for complaint in complaints:
                    data.append(complaint.to_string())
                return response(Commons.SUCCESS, '获取需要审核的投诉记录成功！', data=data)
            except Exception as e:
                return response(Commons.PARAMS_ERROR, '不存在此管理员！')
        else:
            return response(Commons.PARAMS_ERROR, 'token错误！')


# 审核认证
def check_certification(request):
    if request.method != 'POST':
        return response(Commons.METHOD_ERROR, '请求方法错误')
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
                    manager = Manager.objects.get(name=name)
                    try:
                        certification = Certification.objects.get(id=certification_id)
                        if status_code == '1':
                            certification.status = Certification.PASSED
                        elif status_code == '2':
                            certification.status = Certification.REJECTED
                        else:
                            return response(Commons.PARAMS_ERROR, 'status错误！')
                        certification.result_msg = opinion
                    except Exception as e:
                        return response(Commons.PARAMS_ERROR, '不存在此认证记录！')
                except Exception as e:
                    return response(Commons.PARAMS_ERROR, '不存在此管理员！')
            else:
                return response(Commons.PARAMS_ERROR, 'token错误！')
        else:
            return response(Commons.PARAMS_ERROR, '字段不可为空！')


# 审核投诉
def check_complaint(request):
    if request.method != 'POST':
        return response(Commons.METHOD_ERROR, '请求方法错误')
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
                    manager = Manager.objects.get(name=name)
                    try:
                        complaint = Complaint.objects.get(id=complaint_id)
                        if status_code == '1':
                            complaint.status = Complaint.PASSED
                        elif status_code == '2':
                            complaint.status = Complaint.REJECTED
                        else:
                            return response(Commons.PARAMS_ERROR, 'status错误！')
                        complaint.result_msg = opinion
                    except Exception as e:
                        return response(Commons.PARAMS_ERROR, '不存在此投诉记录！')
                except Exception as e:
                    return response(Commons.PARAMS_ERROR, '不存在此管理员！')
            else:
                return response(Commons.PARAMS_ERROR, 'token错误！')
        else:
            return response(Commons.PARAMS_ERROR, '字段不可为空！')
