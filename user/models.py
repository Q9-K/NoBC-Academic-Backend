from django.db import models
from author.models import Author
from work.models import Work


# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    email = models.EmailField(default='暂无', primary_key=True)
    histories = models.ManyToManyField(to='work.Work', through='History', related_name='history_user')
    favorites = models.ManyToManyField(to='work.Work', related_name='favorite_user')
    scholar_identity = models.ForeignKey(to='author.Author', on_delete=models.CASCADE, null=True)
    concept_focus = models.ManyToManyField(to='concept.Concept', related_name='focus_user')
    salt = models.CharField(max_length=4, default='')
    follows = models.ManyToManyField(to='author.Author', related_name='fans')
    # 是否成功注册
    is_active = models.BooleanField(default=False)

    # 个人信息
    real_name = models.CharField(max_length=20, default='暂无')
    gender = models.CharField(max_length=4, default='暂无')
    position = models.CharField(max_length=20, default='暂无')
    organization = models.CharField(max_length=20, default='暂无')
    subject = models.CharField(max_length=20, default='暂无')

    def activate(self):
        """
        激活用户
        """
        self.is_active = True
        self.save()

    def to_string(self):
        return {
            'name': self.name,
            'real_name': self.real_name,
            'gender': self.gender,
            'position': self.position,
            'organization': self.organization,
            'subject': self.subject
        }


class History(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    work = models.ForeignKey(to='work.Work', on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True, primary_key=True)
