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

# Abstract Models


class IndividualTestAbstract(SlugifiedBaseModal):
    status = models.CharField(
        choices=STATUS, help_text='What is current status of this test?')
    test = models.OneToOneField(
        'Test', help_text='Select Parent Test', on_delete=models.CASCADE)
    name = models.CharField(
        max_length=200, help_text='Test ideentifier name. e.g. Art and Science')

    class Meta:
        abstract = True


class IndividualSectionAbstract(SlugifiedBaseModal):
    SECTION = (
        ('section1', 'Section 1'),
        ('section2', 'Section 2'),
        ('section3', 'Section 3'),
        ('section4', 'Section 4'),
    )

    section = models.CharField(
        choices=SECTION, help_text='What is section type?')

    class Meta:
        abstract = True

# Ends: Abstract Models


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


class ListeningTest(IndividualTestAbstract):

    def __str__(self):
        return self.name

    def clean(self):
        if self.status == "error-check":
            for section in self.sections.all():
                check_answers_json(section)

    @property
    def sections(self):
        return ListeningSection.objects.filter(parent_test=self)


class ListeningSection(IndividualSectionAbstract):
    # 4 section: each section has 10 questions.
    parent_test = models.ForeignKey(
        ListeningTest, on_delete=models.CASCADE, help_text='Select Parent Test for this section')
    audio = models.FileField(help_text='Add Audio file for this section')
    questions = RichTextUploadingField(help_text='Add Question in HTML Format')
    answers = models.JSONField(
        help_text='Add 40 answers in JSON format only.', default=get_listening_answer_default)

    def __str__(self):
        return f'{self.parent_test.name} - {self.section}'

# Needs to implement post_save()
def check_answers_json(instance):
    answers = instance.answers
    for item in answers:
        # {'question': 0, 'answer': [None]}
        print(item)
        if not item.get('question'):
            raise ValidationError(
                f"Some of questions are not correctly marked: {item}")
        else:
            if not item.get('answer'):
                raise ValidationError(
                    f"Some of answers contains null values: {item}"
                )
            else:
                for answer in item.get('answer'):
                    if not answer:
                        raise ValidationError(
                            f"Some of answers contains null values: {item}"
                        )
