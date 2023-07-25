from django.db import models
from KeenIeltsDjango.models import SlugifiedBaseModal
from coachinginstitute.models import CoachingInstitute


class Category(SlugifiedBaseModal):
    name = models.CharField(
        max_length=200, help_text='Enter name of the Category')
    website = models.URLField(
        max_length=200, help_text='Enter URL of this Category', null=True, blank=True)
    copyright = models.CharField(
        max_length=300, help_text='Enter copyright information for this category.')

    def __str__(self):
        return self.name


class Test(SlugifiedBaseModal):
    DIFFICULTY = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    is_approved = models.BooleanField(
        default=False, help_text='Is this test approved for public?')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, help_text='Select Category for this Test.')
    difficulty = models.CharField(
        choices=DIFFICULTY, max_length=200, help_text='Difficulty level of this test')
    institute = models.ForeignKey(
        CoachingInstitute, on_delete=models.SET_NULL, blank=False, null=True, help_text='Which institute has created this test?')
    
