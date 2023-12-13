from django.db import models


# Create your models here.

class Work(models.Model):
    id = models.CharField(primary_key=True, max_length=50)

    def to_string(self):
        return {
            'id': self.id,
        }
