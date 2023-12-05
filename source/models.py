from django.db import models


# Create your models here.
class Source(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    display_name = models.TextField()
    views = models.IntegerField(default=0)

    def to_string(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'views': self.views
        }

