from django.db import models

# Create your models here.
class Label(models.Model):
    name = models.CharField(max_length=20)
    labels1 = models.ManyToManyField(to='paper.Paper1', related_name='labels1')
    labels2 = models.ManyToManyField(to='paper.Paper2', related_name='labels2')
    labels3 = models.ManyToManyField(to='paper.Paper3', related_name='labels3')
    labels4 = models.ManyToManyField(to='paper.Paper4', related_name='labels4')
    labels5 = models.ManyToManyField(to='paper.Paper5', related_name='labels5')
    labels6 = models.ManyToManyField(to='paper.Paper6', related_name='labels6')
    labels7 = models.ManyToManyField(to='paper.Paper7', related_name='labels7')
    labels8 = models.ManyToManyField(to='paper.Paper8', related_name='labels8')
    labels9 = models.ManyToManyField(to='paper.Paper9', related_name='labels9')
    labels10 = models.ManyToManyField(to='paper.Paper10', related_name='labels10')

class Paper(models.Model):
    oag_id = models.CharField(max_length=40, primary_key=True)
    title = models.TextField(null=True)

    year = models.IntegerField(default=0, null=True)
    keywords = models.TextField(null=True)
    n_citation = models.IntegerField(default=0, null=True)
    doc_type = models.TextField(null=True)
    publisher = models.TextField(null=True)
    volume = models.TextField(null=True)
    issn = models.TextField(null=True)
    isbn = models.TextField(null=True)
    doi = models.TextField(null=True)
    pdf_url = models.TextField(null=True)
    abstract = models.TextField(default='', null=True)


    class Meta:
        abstract = True


class Paper1(Paper):
    class Meta:
        db_table = 'paper_1'

class Paper2(Paper):
    class Meta:
        db_table = 'paper_2'


class Paper3(Paper):
    class Meta:
        db_table = 'paper_3'


class Paper4(Paper):
    class Meta:
        db_table = 'paper_4'


class Paper5(Paper):
    class Meta:
        db_table = 'paper_5'


class Paper6(Paper):
    class Meta:
        db_table = 'paper_6'


class Paper7(Paper):
    class Meta:
        db_table = 'paper_7'


class Paper8(Paper):
    class Meta:
        db_table = 'paper_8'


class Paper9(Paper):
    class Meta:
        db_table = 'paper_9'


class Paper10(Paper):
    class Meta:
        db_table = 'paper_10'


class Venue(models.Model):
    oag_id = models.CharField(max_length=40)
    journalId = models.CharField(max_length=40)
    displayName = models.CharField(max_length=40)

