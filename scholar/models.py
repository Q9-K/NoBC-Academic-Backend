from django.db import models
from paper.models import Paper

# Create your models here.
class Tag1(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar1 = models.ForeignKey(to='scholar.Scholar1', null=True, related_name='tags1', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)
class Tag2(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar2 = models.ForeignKey(to='scholar.Scholar2', null=True, related_name='tags2', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag3(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar3 = models.ForeignKey(to='scholar.Scholar3', null=True, related_name='tags3', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag4(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar4 = models.ForeignKey(to='scholar.Scholar4', null=True, related_name='tags4', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag5(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar5 = models.ForeignKey(to='scholar.Scholar5', null=True, related_name='tags5', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag6(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar6 = models.ForeignKey(to='scholar.Scholar6', null=True, related_name='tags6', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag7(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar7 = models.ForeignKey(to='scholar.Scholar7', null=True, related_name='tags7', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag8(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar8 = models.ForeignKey(to='scholar.Scholar8', null=True, related_name='tags8', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag9(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar9 = models.ForeignKey(to='scholar.Scholar9', null=True, related_name='tags9', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag10(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar10 = models.ForeignKey(to='scholar.Scholar10', null=True, related_name='tags10', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag11(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar11 = models.ForeignKey(to='scholar.Scholar11', null=True, related_name='tags11', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag12(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar12 = models.ForeignKey(to='scholar.Scholar12', null=True, related_name='tags12', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)

class Tag13(models.Model):
    label = models.ForeignKey(to='paper.Label', on_delete=models.CASCADE)
    scholar13 = models.ForeignKey(to='scholar.Scholar13', null=True, related_name='tags13', on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)


class Scholar(models.Model):
    oag_id = models.CharField(max_length=40, primary_key=True)
    name = models.TextField(null=True)
    organizations = models.TextField(null=True)
    last_org = models.TextField(null=True)
    position = models.TextField(null=True)
    # 论文发表数目
    n_pubs = models.IntegerField(default=0)
    n_citation = models.IntegerField(default=0)
    h_index = models.IntegerField(default=0)
    # 论文
    paper1 = models.ManyToManyField(to='paper.Paper1')
    paper2 = models.ManyToManyField(to='paper.Paper2')
    paper3 = models.ManyToManyField(to='paper.Paper3')
    paper4 = models.ManyToManyField(to='paper.Paper4')
    paper5 = models.ManyToManyField(to='paper.Paper5')
    paper6 = models.ManyToManyField(to='paper.Paper6')
    paper7 = models.ManyToManyField(to='paper.Paper7')
    paper8 = models.ManyToManyField(to='paper.Paper8')
    paper9 = models.ManyToManyField(to='paper.Paper9')
    paper10 = models.ManyToManyField(to='paper.Paper10')

    class Meta:
        abstract = True


class Scholar1(Scholar):
    # 学者合作关系
    partner1 = models.ManyToManyField(to='self', symmetrical=False)
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_1'


class Scholar2(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='self', symmetrical=False)
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_2'


class Scholar3(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='self', symmetrical=False)
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_3'


class Scholar4(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='self', symmetrical=False)
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_4'


class Scholar5(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='self', symmetrical=False)
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_5'
    

class Scholar6(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='self', symmetrical=False)
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_6'


class Scholar7(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='self', symmetrical=False)
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_7'


class Scholar8(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='self', symmetrical=False)
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_8'


class Scholar9(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='self', symmetrical=False)
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_9'


class Scholar10(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='self', symmetrical=False)
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_10'


class Scholar11(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='self', symmetrical=False)
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_11'


class Scholar12(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='self', symmetrical=False)
    partner13 = models.ManyToManyField(to='Scholar13')
    class Meta:
        db_table = 'scholar_12'


class Scholar13(Scholar):
    partner1 = models.ManyToManyField(to='Scholar1')
    partner2 = models.ManyToManyField(to='Scholar2')
    partner3 = models.ManyToManyField(to='Scholar3')
    partner4 = models.ManyToManyField(to='Scholar4')
    partner5 = models.ManyToManyField(to='Scholar5')
    partner6 = models.ManyToManyField(to='Scholar6')
    partner7 = models.ManyToManyField(to='Scholar7')
    partner8 = models.ManyToManyField(to='Scholar8')
    partner9 = models.ManyToManyField(to='Scholar9')
    partner10 = models.ManyToManyField(to='Scholar10')
    partner11 = models.ManyToManyField(to='Scholar11')
    partner12 = models.ManyToManyField(to='Scholar12')
    partner13 = models.ManyToManyField(to='self', symmetrical=False)
    class Meta:
        db_table = 'scholar_13'










































