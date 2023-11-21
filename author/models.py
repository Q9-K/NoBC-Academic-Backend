from django.db import models
from work.models import Work


# Create your models here.
class Author(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    display_name = models.TextField()
    views = models.IntegerField(default=0)
    institution = models.TextField(default='暂无')
    concepts = models.TextField(default='暂无')
    img_url = models.TextField(default='暂无')

    def to_string(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'views': self.views,
        }
