from django.db import models
from author.models import Author
from work.models import Work


# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    email = models.EmailField(default='暂无', primary_key=True)
    histories = models.ManyToManyField(to='work.Work', through='History', related_name='user_history')
    favorites = models.ManyToManyField(to='work.Work', related_name='user_favorite')
    scholar_identity = models.ForeignKey(to='author.Author', on_delete=models.CASCADE, null=True)
    concept_focus = models.ManyToManyField(to='concept.Concept', related_name='user')
    salt = models.CharField(max_length=4, default='')
    follows = models.ManyToManyField(to='author.Author', related_name='fans')
    # 是否成功注册
    is_active = models.BooleanField(default=False)

    def activate(self):
        """
        激活用户
        """
        self.is_active = True
        self.save()


class History(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='work.Work', on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
