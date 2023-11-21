from django.db import models
from user.models import User
from author.models import Author


# Create your models here.
class Message(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField(default='')
    receiver = models.ForeignKey(to='user.User', related_name='msg', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

    def to_string(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'receiver': self.receiver.name,
            'create_time': self.create_time
        }


class Certification(models.Model):
    user = models.ForeignKey(to='user.User', related_name='certification', on_delete=models.CASCADE)
    # 只记录需要认证的学者信息
    scholar = models.TextField(default='')
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
    date_time = models.DateTimeField(auto_now_add=True)

    def to_string(self):
        return {
            'id': self.id,
            'user': self.user.name,
            'author': self.scholar,
            'status': self.get_status_display(),
            'result_msg': self.result_msg,
            'idcard_img_url': self.idcard_img_url,
            'date_time': self.date_time
        }


class Complaint(models.Model):
    user = models.ForeignKey(to='user.User', related_name='complaint', on_delete=models.CASCADE)
    to_scholar = models.TextField(default='')
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
    date_time = models.DateTimeField(auto_now_add=True)

    def to_string(self):
        return {
            'id': self.id,
            'user': self.user.name,
            'to_scholar': self.to_scholar,
            'status': self.get_status_display(),
            'result_msg': self.result_msg,
            'complaint_content': self.complaint_content,
            'date_time': self.date_time
        }
