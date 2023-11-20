from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models
from django.core.mail import send_mail


class User(BaseUser):
    objects = BaseUserManager()
    verification_code = models.PositiveIntegerField(
        null=True, blank=True, help_text='Verification code sent to user email')
    is_verified = models.BooleanField(
        default=False, help_text='Is user email verified?')

    def save(self, *args, **kwargs):
        self.generate_verification_code()
        if not self.pk:  # Only generate verification code for new users

            pass
        super().save(*args, **kwargs)

    def generate_verification_code(self):
        import random
        otp = random.randint(100000, 999999)
        self.verification_code = otp
        self.send_verification_code_email(otp)
        return otp

    def send_verification_code_email(self, code):
        print('Sending email')
        send_mail(
            subject='KeenIELTS Verification Code',
            message=f'Your verification code is {code}',
            from_email='KeenIELTS <notifications@zepto.keenielts.com>',
            recipient_list=[self.email, ],
            fail_silently=False,
        )

        return True
