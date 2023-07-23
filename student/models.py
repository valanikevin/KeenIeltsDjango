from django.db import models
from django.contrib.auth import get_user_model
from coachinginstitute.models import CoachingInstitute
from KeenIeltsDjango.models import SlugifiedBaseModal


class Student(SlugifiedBaseModal):
    user = models.OneToOneField(get_user_model(
    ), on_delete=models.CASCADE, help_text='Select base user for this student.')
    institute = models.ForeignKey(CoachingInstitute, on_delete=models.SET_NULL, null=True,
                                  blank=True, help_text="Is this student enrolled at any coaching institute?")

    def __str__(self):
        return self.user.email
