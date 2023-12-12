from django.db import models


# Create your models here.
class Institution(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
