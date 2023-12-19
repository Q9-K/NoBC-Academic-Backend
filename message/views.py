from utils.Response import response
from NoBC.status_code import *


# Create your views here.
def apply_for_certification(request):
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        email = request.POST.get('email', None)
        scholar_id = request.POST.get('scholar_id', None)
