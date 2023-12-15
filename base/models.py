from django.db import models
from KeenIeltsDjango.models import TimestampedBaseModel
from django.conf import settings

# Create your models here.


class Issue(TimestampedBaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    description = models.TextField(help_text="Describe the issue in detail")
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.email} | {self.type}'
