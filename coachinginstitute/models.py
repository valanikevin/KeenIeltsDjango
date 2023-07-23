from django.db import models
from django.contrib.auth import get_user_model
from KeenIeltsDjango.models import SlugifiedBaseModal
# Create your models here.


class CoachingInstitute(SlugifiedBaseModal):
    is_verified = models.BooleanField(
        default=False, help_text='Is this school verified for green tick?')
    name = models.CharField(
        max_length=200, help_text='Name of this institute.')
    email = models.EmailField(
        help_text="Primary email of this institute.", max_length=254)
    phone = models.CharField(
        help_text="Primary phone number of this institute.", max_length=50)
    logo = models.ImageField(
        help_text="Logo of this institute")

    def __str__(self):
        return self.name


class Tutor(models.Model):
    user = models.OneToOneField(get_user_model(
    ), on_delete=models.CASCADE, help_text='Select base user')
    institute = models.ForeignKey(
        CoachingInstitute, help_text='Is this Tutor part of any Coaching Institute?', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email
