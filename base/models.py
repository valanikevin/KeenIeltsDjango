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


class CommentMain(models.Model):
    unique_id = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.unique_id

    def comments(self):
        return self.commentitem_set.order_by('-id')[:30]


class CommentItem(TimestampedBaseModel):
    main = models.ForeignKey(CommentMain, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    comment = models.TextField(help_text="Enter your comment here")

    def __str__(self):
        return f'{self.user.email} | {self.comment}'


class AiResponse(TimestampedBaseModel):
    STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    )
    status = models.CharField(
        max_length=100, choices=STATUS, default='pending')
    info = models.CharField(
        max_length=500, help_text="Info about this AI response")
    input = models.TextField(help_text="Input to the AI")
    response = models.TextField(help_text="Response from the AI")

    def __str__(self):
        return f'{self.info} '
