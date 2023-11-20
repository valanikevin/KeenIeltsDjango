from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models


class User(BaseUser):
    objects = BaseUserManager()
    verification_code = models.PositiveIntegerField(
        null=True, blank=True, help_text='Verification code sent to user email')
    is_verified = models.BooleanField(
        default=False, help_text='Is user email verified?')

    def generate_verification_code(self):
        import random
        otp = random.randint(100000, 999999)
        self.verification_code = otp
        return otp
