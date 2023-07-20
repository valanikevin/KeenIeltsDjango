from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models


class User(BaseUser):
    objects = BaseUserManager()


class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
