from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models


class User(BaseUser):
    objects = BaseUserManager()
    is_verified = models.BooleanField(
        default=False, help_text='Is user email verified?')
