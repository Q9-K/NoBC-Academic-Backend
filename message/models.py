from django.db import models
from user.models import User
from scholar.models import Scholar

# Create your models here.
class Message(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField(default='')
    receiver = models.ForeignKey(to='user.User', related_name='msg', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

class Certification(models.Model):
    user = models.ForeignKey(to='user.User', related_name='ca', on_delete=models.CASCADE)
    to_scholar1 = models.ForeignKey(to='scholar.Scholar1', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar2 = models.ForeignKey(to='scholar.Scholar2', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar3 = models.ForeignKey(to='scholar.Scholar3', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar4 = models.ForeignKey(to='scholar.Scholar4', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar5 = models.ForeignKey(to='scholar.Scholar5', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar6 = models.ForeignKey(to='scholar.Scholar6', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar7 = models.ForeignKey(to='scholar.Scholar7', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar8 = models.ForeignKey(to='scholar.Scholar8', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar9 = models.ForeignKey(to='scholar.Scholar9', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar10 = models.ForeignKey(to='scholar.Scholar10', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar11 = models.ForeignKey(to='scholar.Scholar11', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar12 = models.ForeignKey(to='scholar.Scholar12', related_name='ca', null=True, on_delete=models.CASCADE)
    to_scholar13 = models.ForeignKey(to='scholar.Scholar13', related_name='ca', null=True, on_delete=models.CASCADE)
    # 状态可选项
    PENDING = 'PD'
    PASSED = 'PS'
    REJECTED = 'RJ'
    STATUS_IN_CHOICE = [
        (PENDING, 'pending'),
        (PASSED, 'processed'),
        (REJECTED, 'rejected')
    ]
    status = models.CharField(max_length=2, choices=STATUS_IN_CHOICE, default=PENDING)
    result_msg = models.TextField(default='')
    idcard_img_url = models.CharField(max_length=50, default='')

class Complaint(models.Model):
    user = models.ForeignKey(to='user.User', related_name='cp', on_delete=models.CASCADE)
    to_scholar1 = models.ForeignKey(to='scholar.Scholar1', null=True, on_delete=models.CASCADE)
    to_scholar2 = models.ForeignKey(to='scholar.Scholar2', null=True, on_delete=models.CASCADE)
    to_scholar3 = models.ForeignKey(to='scholar.Scholar3', null=True, on_delete=models.CASCADE)
    to_scholar4 = models.ForeignKey(to='scholar.Scholar4', null=True, on_delete=models.CASCADE)
    to_scholar5 = models.ForeignKey(to='scholar.Scholar5', null=True, on_delete=models.CASCADE)
    to_scholar6 = models.ForeignKey(to='scholar.Scholar6', null=True, on_delete=models.CASCADE)
    to_scholar7 = models.ForeignKey(to='scholar.Scholar7', null=True, on_delete=models.CASCADE)
    to_scholar8 = models.ForeignKey(to='scholar.Scholar8', null=True, on_delete=models.CASCADE)
    to_scholar9 = models.ForeignKey(to='scholar.Scholar9', null=True, on_delete=models.CASCADE)
    to_scholar10 = models.ForeignKey(to='scholar.Scholar10', null=True, on_delete=models.CASCADE)
    to_scholar11 = models.ForeignKey(to='scholar.Scholar11', null=True, on_delete=models.CASCADE)
    to_scholar12 = models.ForeignKey(to='scholar.Scholar12', null=True, on_delete=models.CASCADE)
    to_scholar13 = models.ForeignKey(to='scholar.Scholar13', null=True, on_delete=models.CASCADE)
    # 状态可选项
    PENDING = 'PD'
    PASSED = 'PS'
    REJECTED = 'RJ'
    STATUS_IN_CHOICE = [
        (PENDING, 'pending'),
        (PASSED, 'processed'),
        (REJECTED, 'rejected')
    ]
    status = models.CharField(max_length=2, choices=STATUS_IN_CHOICE, default=PENDING)
    result_msg = models.TextField(default='')
    complaint_content = models.TextField()