from django.db import models
from KeenIeltsDjango.models import SlugifiedBaseModal, TimestampedBaseModel
from coachinginstitute.models import CoachingInstitute
from ckeditor_uploader.fields import RichTextUploadingField
from ieltstest.answer_json.listening import get_listening_answer_default
from django.core.exceptions import ValidationError

STATUS = (
    ('draft', 'Draft'),
    ('in-progress', 'In Progress'),
    ('error-check', 'Perform Error Check'),
    ('error-found', 'Error Found'),
    ('published', 'Published'),
    ('discard', 'Discard')
)

TEST_TYPE = (
    ('academic', 'Academic'),
    ('general', 'General'),
    ('both', 'Both')
)

# Abstract Models


class IndividualModuleAbstract(SlugifiedBaseModal):
    test_type = models.CharField(
        max_length=200, help_text='What is test type for this?', choices=TEST_TYPE)
    test = models.OneToOneField(
        'Test', help_text='Select Parent Test', on_delete=models.CASCADE,)
    status = models.CharField(
        choices=STATUS, help_text='What is current status of this test?', max_length=200)
    name = models.CharField(
        max_length=200, help_text='e.g. Listening Test March 2023')

    class Meta:
        abstract = True


class IndividualModuleSectionAbstract(models.Model):
    SECTION = (
        ('section1', 'Section 1'),
        ('section2', 'Section 2'),
        ('section3', 'Section 3'),
        ('section4', 'Section 4'),
    )
    section = models.CharField(
        choices=SECTION, help_text='What is section type?')
    name = models.CharField(
        max_length=200, help_text='Test ideentifier name. e.g. Art and Science')

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.name} - {self.section}'


class Book(SlugifiedBaseModal, TimestampedBaseModel):
    DIFFICULTY = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    name = models.CharField(
        max_length=200, help_text='What is name of the book?')
    description = models.TextField(help_text="Add small book description.")
    difficulty = models.CharField(
        choices=DIFFICULTY, max_length=200, help_text='Difficulty level of this test')
    cover = models.ImageField(
        help_text='Image of the Book Cover', null=True, blank=True)
    institute = models.ForeignKey(
        CoachingInstitute, on_delete=models.SET_NULL, blank=False, null=True, help_text='Which institute has created this test?')
    website = models.URLField(
        max_length=200, help_text='Enter URL of this Category', null=True, blank=True)
    copyright = models.CharField(
        max_length=300, help_text='Enter copyright information for this category.')

    def __str__(self):
        return self.name

    @property
    def tests(self):
        return Test.objects.filter(book=self)

    @property
    def tests_with_listening_module(self):
        tests = self.tests
        tests_ids = []
        for test in tests:
            if test.listening_module.exists():
                tests_ids.append(test.id)

        tests = self.tests.filter(pk__in=tests_ids)
        return tests


class Test(SlugifiedBaseModal, TimestampedBaseModel):
    book = models.ForeignKey(
        Book, help_text='Select book for this test', on_delete=models.CASCADE)
    status = models.CharField(
        choices=STATUS, help_text='What is current status of this test?')
    name = models.CharField(
        max_length=200, help_text='e.g. Practise Test 1')

    def __str__(self):
        return self.name

    @property
    def listening_module(self):
        return ListeningModule.objects.filter(test=self)


class ListeningModule(IndividualModuleAbstract):

    def __str__(self):
        return self.test.name if self.test else ""

    @property
    def sections(self):
        return ListeningSection.objects.filter(listening_module=self)


class ListeningSection(IndividualModuleSectionAbstract):
    # 4 section: each section has 10 questions.

    listening_module = models.ForeignKey(
        ListeningModule, on_delete=models.CASCADE, help_text='Select Parent Test for this section')
    audio = models.FileField(help_text='Add Audio file for this section')
    questions = RichTextUploadingField(
        help_text='Add questions with form elements and correct ids')
    answers = models.JSONField(
        help_text='Add answers for the questions above', default=get_listening_answer_default)
