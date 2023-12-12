from django.db import models
from work.models import Work


# Create your models here.
class Author(models.Model):
    id = models.CharField(primary_key=True, max_length=50)

    def to_string(self):
        return {
            'id': self.id,
        }
