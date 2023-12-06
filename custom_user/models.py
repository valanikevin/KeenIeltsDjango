from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from django_rest_passwordreset.signals import reset_password_token_created


class User(BaseUser):
    objects = BaseUserManager()
    verification_code = models.PositiveIntegerField(
        null=True, blank=True, help_text='Verification code sent to user email')
    is_verified = models.BooleanField(
        default=False, help_text='Is user email verified?')

    def save(self, *args, **kwargs):

        if not self.pk:  # Only generate verification code for new users
            self.generate_verification_code()
        super().save(*args, **kwargs)

    def generate_verification_code(self):
        import random
        otp = random.randint(100000, 999999)
        self.verification_code = otp
        self.send_verification_code_email(otp)
        return otp

    def send_verification_code_email(self, code):
        send_mail(
            subject='KeenIELTS Verification Code',
            message=f'Your verification code is {code}',
            from_email='KeenIELTS <notifications@zepto.keenielts.com>',
            recipient_list=[self.email, ],
            fail_silently=True,
        )
        return True


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(
                reverse('password_reset:reset-password-confirm')),
            reset_password_token.key)
    }

    message = f"""
Hi {reset_password_token.user.first_name},
You have requested to reset your password.

Please click on the link below to reset your password:
{context['reset_password_url']}

If you did not request to reset your password, please ignore this email.

- Team KeenIELTS
    """

    send_mail(
        subject='KeenIELTS Password Reset',
        message=message,
        from_email='KeenIELTS <notifications@zepto.keenielts.com>',
        recipient_list=[context['email'], ],
        fail_silently=True,
    )
    return True
