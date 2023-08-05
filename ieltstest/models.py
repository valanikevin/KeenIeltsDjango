from django.db import models
from KeenIeltsDjango.models import SlugifiedBaseModal, TimestampedBaseModel
from coachinginstitute.models import CoachingInstitute
from ckeditor_uploader.fields import RichTextUploadingField
from ieltstest.answer_json.listening import get_listening_answer_default
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

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
    total_questions = models.PositiveIntegerField(
        help_text='How many questions are there in this module?', default=0)

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
    total_questions = models.PositiveIntegerField(
        help_text='How many questions are there in this section?', default=0)

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
    audio = models.FileField(
        help_text='Add Audio file, all section merged in one audio')

    def __str__(self):
        return self.test.name if self.test else ""

    @property
    def sections(self):
        return ListeningSection.objects.filter(listening_module=self).order_by('section')

    def save(self, *args, **kwargs):
        update_form_fields_with_ids(self)
        super(ListeningModule, self).save(*args, **kwargs)


class ListeningSectionQuestionType(models.Model):
    name = models.CharField(
        max_length=200, help_text='Name of the question type. E.g. True/False, Match the topic, etc')

    def __str__(self):
        return self.name


class ListeningSection(IndividualModuleSectionAbstract):
    question_type = models.ForeignKey(
        ListeningSectionQuestionType, on_delete=models.CASCADE, help_text='Choose question type for this section', null=True)
    listening_module = models.ForeignKey(
        ListeningModule, on_delete=models.CASCADE, help_text='Select Parent Test for this section')
    audio_start_time = models.DecimalField(
        decimal_places=2, max_digits=20, default=0.0, help_text='When should audio start for this section? 18.45 (18 seconds)')
    questions = RichTextUploadingField(
        help_text='Add questions with form elements and correct ids')
    answers = models.JSONField(
        help_text='Add answers for the questions above', default=get_listening_answer_default)


class ListeningAttempt(TimestampedBaseModel, SlugifiedBaseModal):
    STATUS = (
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Evaluated', 'Evaluated')
    )
    status = models.CharField(
        choices=STATUS, help_text='What is currect status of this attempt?', default='In Progress')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='Select user for the attempt')
    module = models.ForeignKey(
        ListeningModule, help_text='Select parent module for this attempt', on_delete=models.CASCADE)
    answers = models.JSONField(
        null=True, blank=True, help_text='Answers that is attempted by user')
    evaluation = models.JSONField(
        null=True, blank=True, help_text='Evaluation of the attempt')
    time_taken = models.PositiveIntegerField(
        default=0, help_text='How much time did user take to complete the test? In minutes.')
    bands = models.FloatField(default=0.0, )
    correct_answers = models.PositiveIntegerField(default=0)
    incorrect_answers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user.email} - {self.slug}'

    def save(self, *args, **kwargs):
        if self.status == "Completed":
            attempt = check_listening_answers(self)
            return super(ListeningAttempt, attempt).save(*args, **kwargs)
        return super(ListeningAttempt, self).save(*args, **kwargs)


def update_form_fields_with_ids(module):
    from bs4 import BeautifulSoup
    sections = module.sections
    counter = 0
    for section in sections:
        if section.questions:
            soup = BeautifulSoup(section.questions, 'html.parser')
            form_elements = soup.find_all(['input', 'textarea', 'select'])
            local_counter = 0
            for element in form_elements:
                print(element)
                counter = counter+1
                local_counter = local_counter + 1
                element['id'] = f'que-{counter}'
                element['name'] = f'que-{counter}'
                element['required'] = f'false'
            section.total_questions = local_counter
            section.questions = str(soup)
            section.save()
    if module.total_questions is not counter:
        module.total_questions = counter
        module.save()


def check_listening_answers(attempt):
    complete_evaluation = {}
    evaluation = {}
    counter = 0
    correct_answers_count = 0
    incorrect_answers_count = 0
    for section in attempt.module.sections:
        answers = section.answers
        section_evaluation = {}
        section_correct = 0
        section_incorrect = 0
        for answer in answers:
            _evaluation = {}
            counter = counter + 1
            correct_answer = answer['answer']  # List
            user_answer = str(attempt.answers.get(
                f"que-{counter}"))
            is_user_answer_correct = False
            if any(s.lower() == user_answer.lower() for s in correct_answer):
                is_user_answer_correct = True
                correct_answers_count = correct_answers_count + 1
                section_correct = section_correct + 1
            else:
                incorrect_answers_count = incorrect_answers_count + 1
                section_incorrect = section_incorrect + 1

            _evaluation['correct_answer'] = correct_answer
            _evaluation['user_answer'] = user_answer
            _evaluation['is_user_answer_correct'] = is_user_answer_correct
            evaluation[f'que-{counter}'] = _evaluation
            section_evaluation[f'que-{counter}'] = _evaluation

        section_evaluation['correct'] = section_correct
        section_evaluation['incorrect'] = section_incorrect
        section_evaluation['total_questions'] = section_correct + \
            section_incorrect
        section_evaluation['question_type'] = section.question_type.name

        complete_evaluation[section.section] = section_evaluation

    complete_evaluation['all_questions'] = evaluation

    # Assignments
    timetaken = round(
        (timezone.now() - attempt.created_at).total_seconds() / 60)
    attempt.evaluation = complete_evaluation
    attempt.correct_answers = correct_answers_count
    attempt.incorrect_answers = incorrect_answers_count
    attempt.status = "Evaluated"
    attempt.bands = get_listening_ielts_score(
        correct_answers_count, counter)
    attempt.time_taken = timetaken
    return attempt


def get_listening_ielts_score(correct, total=40):
    score = int((correct/total)*40)
    score_map = {
        39: 9,
        37: 8.5,
        35: 8,
        32: 7.5,
        30: 7,
        26: 6.5,
        23: 6,
        18: 5.5,
        16: 5,
        13: 4.5,
        10: 4,
    }

    for map in score_map:
        if score >= map:
            return score_map[map]

    return 0.0
