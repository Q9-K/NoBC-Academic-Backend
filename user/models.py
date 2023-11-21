from django.db import models
from scholar.models import Scholar
from paper.models import Paper

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=28)
    email = models.EmailField(default='暂无')
    # favorites = models.ManyToManyField(to='paper.Paper', related_name='users')
    histories1 = models.ManyToManyField(to='paper.Paper1', through='HistoryRecord1', related_name='user')
    histories2 = models.ManyToManyField(to='paper.Paper2', through='HistoryRecord2', related_name='user')
    histories3 = models.ManyToManyField(to='paper.Paper3', through='HistoryRecord3', related_name='user')
    histories4 = models.ManyToManyField(to='paper.Paper4', through='HistoryRecord4', related_name='user')
    histories5 = models.ManyToManyField(to='paper.Paper5', through='HistoryRecord5', related_name='user')
    histories6 = models.ManyToManyField(to='paper.Paper6', through='HistoryRecord6', related_name='user')
    histories7 = models.ManyToManyField(to='paper.Paper7', through='HistoryRecord7', related_name='user')
    histories8 = models.ManyToManyField(to='paper.Paper8', through='HistoryRecord8', related_name='user')
    histories9 = models.ManyToManyField(to='paper.Paper9', through='HistoryRecord9', related_name='user')
    histories10 = models.ManyToManyField(to='paper.Paper10', through='HistoryRecord10', related_name='user')

    follows1 = models.ManyToManyField(to='scholar.Scholar1', related_name='fans')
    follows2 = models.ManyToManyField(to='scholar.Scholar2', related_name='fans')
    follows3 = models.ManyToManyField(to='scholar.Scholar3', related_name='fans')
    follows4 = models.ManyToManyField(to='scholar.Scholar4', related_name='fans')
    follows5 = models.ManyToManyField(to='scholar.Scholar5', related_name='fans')
    follows6 = models.ManyToManyField(to='scholar.Scholar6', related_name='fans')
    follows7 = models.ManyToManyField(to='scholar.Scholar7', related_name='fans')
    follows8 = models.ManyToManyField(to='scholar.Scholar8', related_name='fans')
    follows9 = models.ManyToManyField(to='scholar.Scholar9', related_name='fans')
    follows10 = models.ManyToManyField(to='scholar.Scholar10', related_name='fans')
    follows11 = models.ManyToManyField(to='scholar.Scholar11', related_name='fans')
    follows12 = models.ManyToManyField(to='scholar.Scholar12', related_name='fans')
    follows13 = models.ManyToManyField(to='scholar.Scholar13', related_name='fans')

    scholar_identity1 = models.ForeignKey(to='scholar.Scholar1', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity2 = models.ForeignKey(to='scholar.Scholar2', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity3 = models.ForeignKey(to='scholar.Scholar3', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity4 = models.ForeignKey(to='scholar.Scholar4', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity5 = models.ForeignKey(to='scholar.Scholar5', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity6 = models.ForeignKey(to='scholar.Scholar6', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity7 = models.ForeignKey(to='scholar.Scholar7', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity8 = models.ForeignKey(to='scholar.Scholar8', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity9 = models.ForeignKey(to='scholar.Scholar9', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity10 = models.ForeignKey(to='scholar.Scholar10', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity11 = models.ForeignKey(to='scholar.Scholar11', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity12 = models.ForeignKey(to='scholar.Scholar12', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)
    scholar_identity13 = models.ForeignKey(to='scholar.Scholar13', related_name='user', blank=True, null=True,on_delete=models.SET_NULL)

    favorites1 = models.ManyToManyField(to='paper.Paper1', related_name='users')
    favorites2 = models.ManyToManyField(to='paper.Paper2', related_name='users')
    favorites3 = models.ManyToManyField(to='paper.Paper3', related_name='users')
    favorites4 = models.ManyToManyField(to='paper.Paper4', related_name='users')
    favorites5 = models.ManyToManyField(to='paper.Paper5', related_name='users')
    favorites6 = models.ManyToManyField(to='paper.Paper6', related_name='users')
    favorites7 = models.ManyToManyField(to='paper.Paper7', related_name='users')
    favorites8 = models.ManyToManyField(to='paper.Paper8', related_name='users')
    favorites9 = models.ManyToManyField(to='paper.Paper9', related_name='users')
    favorites10 = models.ManyToManyField(to='paper.Paper10', related_name='users')


class HistoryRecord1(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='paper.Paper1', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

class HistoryRecord2(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='paper.Paper2', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

class HistoryRecord3(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='paper.Paper3', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

class HistoryRecord4(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='paper.Paper4', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

class HistoryRecord5(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='paper.Paper5', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

class HistoryRecord6(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='paper.Paper6', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

class HistoryRecord7(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='paper.Paper7', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

class HistoryRecord8(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='paper.Paper8', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

class HistoryRecord9(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='paper.Paper9', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)

class HistoryRecord10(models.Model):
    user = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    paper = models.ForeignKey(to='paper.Paper10', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_created=True)
