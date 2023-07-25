from django.db import models
from KeenIeltsDjango.models import SlugifiedBaseModal, TimestampedBaseModel
from coachinginstitute.models import CoachingInstitute
from ckeditor.fields import RichTextField
from ieltstest.answer_json.listening import get_listening_answer_default


class Category(SlugifiedBaseModal):
    name = models.CharField(
        max_length=200, help_text='Enter name of the Category')
    website = models.URLField(
        max_length=200, help_text='Enter URL of this Category', null=True, blank=True)
    copyright = models.CharField(
        max_length=300, help_text='Enter copyright information for this category.')

    def __str__(self):
        return self.name


class Test(SlugifiedBaseModal, TimestampedBaseModel):
    DIFFICULTY = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    is_approved = models.BooleanField(
        default=False, help_text='Is this test approved for public?')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, help_text='Select Category for this Test.')
    name = models.CharField(
        max_length=200, help_text='What is name of the Test? e.g. Cambridge Complete Test 11')
    difficulty = models.CharField(
        choices=DIFFICULTY, max_length=200, help_text='Difficulty level of this test')
    institute = models.ForeignKey(
        CoachingInstitute, on_delete=models.SET_NULL, blank=False, null=True, help_text='Which institute has created this test?')

    def __str__(self):
        return self.name


class ListeningTest(SlugifiedBaseModal):
    test = models.OneToOneField(
        Test, help_text='Select Parent Test', on_delete=models.CASCADE)
    name = models.CharField(
        max_length=200, help_text='Test ideentifier name. e.g. Art and Science')

    def __str__(self):
        return self.name


class ListeningSection(SlugifiedBaseModal):
    SECTION = (
        ('section1', 'Section 1'),
        ('section2', 'Section 2'),
        ('section3', 'Section 3'),
        ('section4', 'Section 4'),
    )

    parent_test = models.ForeignKey(
        ListeningTest, on_delete=models.CASCADE, help_text='Select Parent Test for this section')
    section = models.CharField(
        choices=SECTION, help_text='What is section type?')
    audio = models.FileField(help_text='Add Audio file for this section')
    questions = RichTextField(help_text='Add Question in HTML Format')
    answers = models.JSONField(
        help_text='Add 40 answers in JSON format only.', default=get_listening_answer_default)

    def __str__(self):
        return f'{self.parent_test.name} - {self.section}'
