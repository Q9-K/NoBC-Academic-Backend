from utils.Response import response
from NoBC.status_code import *
from utils.view_decorator import login_required, allowed_methods


# Create your views here.
@allowed_methods(['POST'])
@login_required
def apply_for_certification(request):
    pass

