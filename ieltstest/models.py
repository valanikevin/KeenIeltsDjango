from django.db import models
from KeenIeltsDjango.models import SlugifiedBaseModal, TimestampedBaseModel
from coachinginstitute.models import CoachingInstitute
from ckeditor_uploader.fields import RichTextUploadingField
from ieltstest.answer_json.listening import get_listening_answer_default
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
import openai
from ieltstest.openai import writing_prompts

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
        ('Section 1', 'Section 1'),
        ('Section 2', 'Section 2'),
        ('Section 3', 'Section 3'),
        ('Section 4', 'Section 4'),
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


class IndividualModuleAttemptAbstract(TimestampedBaseModel, SlugifiedBaseModal):
    STATUS = (
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Evaluated', 'Evaluated')
    )
    status = models.CharField(
        choices=STATUS, help_text='What is currect status of this attempt?', default='In Progress')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='Select user for the attempt')
    evaluation = models.JSONField(
        null=True, blank=True, help_text='Evaluation of the attempt')
    time_taken = models.PositiveIntegerField(
        default=0, help_text='How much time did user take to complete the test? In minutes.')
    bands = models.FloatField(default=0.0, )

    def __str__(self):
        return f'{self.user.email} - {self.slug}'

    class Meta:
        abstract = True


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
        tests = self.tests.filter(listeningmodule__test__isnull=False)
        return tests

    def tests_with_reading_module(self, user):
        student_type = user.student.type if user.id else None
        if student_type:
            tests = self.tests.filter(
                readingmodule__test__isnull=False, readingmodule__test_type=student_type)
        else:
            tests = self.tests.filter(readingmodule__test__isnull=False)

        return tests

    def tests_with_writing_module(self, user):
        student_type = user.student.type if user.id else None
        if student_type:
            tests = self.tests.filter(
                writingmodule__test__isnull=False, writingmodule__test_type=student_type)
        else:
            tests = self.tests.filter(writingmodule__test__isnull=False)

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


class QuestionType(models.Model):
    name = models.CharField(
        max_length=200, help_text='Name of the question type. E.g. True/False, Match the topic, etc')

    def __str__(self):
        return self.name


class ListeningSection(IndividualModuleSectionAbstract):
    question_type = models.ForeignKey(
        QuestionType, on_delete=models.CASCADE, help_text='Choose question type for this section', null=True)
    listening_module = models.ForeignKey(
        ListeningModule, on_delete=models.CASCADE, help_text='Select Parent Test for this section')
    audio_start_time = models.DecimalField(
        decimal_places=2, max_digits=20, default=0.0, help_text='When should audio start for this section? 18.45 (18 seconds)')
    questions = RichTextUploadingField(
        help_text='Add questions with form elements and correct ids')
    answers = models.JSONField(
        help_text='Add answers for the questions above', default=get_listening_answer_default)


class ListeningAttempt(IndividualModuleAttemptAbstract):
    module = models.ForeignKey(
        ListeningModule, help_text='Select parent module for this attempt', on_delete=models.CASCADE)
    answers = models.JSONField(
        null=True, blank=True, help_text='Answers that is attempted by user')
    correct_answers = models.PositiveIntegerField(default=0)
    incorrect_answers = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.status == "Completed":
            attempt = check_answers(self)
            attempt.bands = get_listening_ielts_score(
                attempt.correct_answers, attempt.correct_answers+attempt.incorrect_answers)
            return super(ListeningAttempt, attempt).save(*args, **kwargs)
        return super(ListeningAttempt, self).save(*args, **kwargs)


class ReadingAttempt(IndividualModuleAttemptAbstract):
    module = models.ForeignKey(
        'ReadingModule', help_text='Select Parent module for this attempt', on_delete=models.CASCADE)
    answers = models.JSONField(
        null=True, blank=True, help_text='Answers that is attempted by user')
    correct_answers = models.PositiveIntegerField(default=0)
    incorrect_answers = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.status == "Completed":
            attempt = check_answers(self)
            if attempt.module.test_type == 'academic':
                attempt.bands = get_reading_academic_ielts_score(
                    attempt.correct_answers, attempt.correct_answers+attempt.incorrect_answers)
            else:
                attempt.bands = get_reading_general_ielts_score(
                    attempt.correct_answers, attempt.correct_answers+attempt.incorrect_answers)
            return super(ReadingAttempt, attempt).save(*args, **kwargs)
        return super(ReadingAttempt, self).save(*args, **kwargs)


class ReadingModule(IndividualModuleAbstract):

    def __str__(self):
        return self.test.name if self.test else ""

    def save(self, *args, **kwargs):
        update_form_fields_with_ids(self)
        super(ReadingModule, self).save(*args, **kwargs)

    @property
    def sections(self):
        return ReadingSection.objects.filter(reading_module=self).order_by('section')


class ReadingSection(IndividualModuleSectionAbstract):
    question_type = models.ForeignKey(
        QuestionType, on_delete=models.CASCADE, help_text='Choose question type for this section', null=True)
    reading_module = models.ForeignKey(
        ReadingModule, on_delete=models.CASCADE, help_text='Select parent reading module')
    passage = RichTextUploadingField(
        help_text='Add passage for this section')
    questions = RichTextUploadingField(
        help_text='Add questions with form elements and correct ids')
    answers = models.JSONField(
        help_text='Add answers for the questions above', default=get_listening_answer_default)

    def __str__(self):
        return self.name


class WritingModule(IndividualModuleAbstract):
    def __str__(self):
        return self.test.name if self.test else ""

    @property
    def sections(self):
        return WritingSection.objects.filter(writing_module=self).order_by('section')


class WritingSection(IndividualModuleSectionAbstract):
    question_type = models.ForeignKey(
        QuestionType, on_delete=models.CASCADE, help_text='Choose question type for this section', null=True)
    writing_module = models.ForeignKey(
        WritingModule, on_delete=models.CASCADE, help_text='Select parent writing module')
    task = RichTextUploadingField(
        help_text='Add task 1/2 with images for writing module')
    questions = RichTextUploadingField(
        help_text='Add questions/text area for user to write answer')

    def __str__(self):
        return self.name


class WritingAttempt(IndividualModuleAttemptAbstract):
    module = models.ForeignKey(
        'WritingModule', help_text='Select Parent module for this attempt', on_delete=models.CASCADE)
    answers = models.JSONField(
        null=True, blank=True, help_text='Answers that is attempted by user')

    def save(self, *args, **kwargs):
        attempt = evaluate_writing_attempt(self)
        if self.status == "Completed":
            return super(WritingAttempt, attempt).save(*args, **kwargs)
        return super(WritingAttempt, self).save(*args, **kwargs)


# Speaking Module
# Speaking Section
# Speaking Attempt


def update_form_fields_with_ids(module):
    from bs4 import BeautifulSoup
    sections = module.sections
    counter = 0
    processed_radio_names = {}
    for section in sections:
        if section.questions:
            soup = BeautifulSoup(section.questions, 'html.parser')
            form_elements = soup.find_all(['input', 'textarea', 'select'])
            local_counter = 0
            for element in form_elements:
                if element.name == 'input' and element.get('type') == 'radio':
                    radio_name = element['name']
                    print(f'RADIO: {radio_name}')
                    if processed_radio_names.get(radio_name):
                        element['name'] = f'que-{processed_radio_names.get(radio_name)}'
                        element['required'] = f'false'
                    else:
                        counter = counter + 1
                        processed_radio_names[radio_name] = counter
                        element['name'] = f'que-{counter}'
                        element['required'] = f'false'

                else:
                    counter = counter+1
                    local_counter = local_counter + 1
                    # element['id'] = f'que-{counter}'
                    element['name'] = f'que-{counter}'
                    element['required'] = f'false'
                print(element)
            section.total_questions = local_counter
            section.questions = str(soup)
            section.save()

    if module.total_questions is not counter:
        module.total_questions = counter
        module.save()


def check_answers(attempt):
    complete_evaluation = {}
    evaluation = {}
    sections = []
    counter = 0
    correct_answers_count = 0
    incorrect_answers_count = 0
    best_scored_section = ('', 0)
    worst_scored_section = ('', float('inf'))

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
        sections.append(section_evaluation)

        # Update best and worst scored sections if needed
        if section_correct > best_scored_section[1]:
            best_scored_section = (section.section, section_correct)
        if section_correct < worst_scored_section[1]:
            worst_scored_section = (section.section, section_correct)

    complete_evaluation['all_questions'] = evaluation
    complete_evaluation['all_sections'] = sections

    # Add the best and worst scored sections to the evaluation
    complete_evaluation['best_scored_section'] = best_scored_section
    complete_evaluation['worst_scored_section'] = worst_scored_section

    # Assignments
    timetaken = round(
        (timezone.now() - attempt.created_at).total_seconds() / 60)
    attempt.evaluation = complete_evaluation
    attempt.correct_answers = correct_answers_count
    attempt.incorrect_answers = incorrect_answers_count
    attempt.status = "Evaluated"

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
        0: 0,
    }

    for map in score_map:
        if score >= map:
            return score_map[map]

    return 0.0


def get_reading_academic_ielts_score(correct, total=40):
    score = int((correct/total)*40)
    score_map = {
        39: 9,
        37: 8.5,
        35: 8,
        33: 7.5,
        30: 7,
        27: 6.5,
        23: 6,
        19: 5.5,
        15: 5,
        13: 4.5,
        10: 4,
        0: 0,
    }

    for map in score_map:
        if score >= map:
            return score_map[map]

    return 0.0


def get_reading_general_ielts_score(correct, total=40):
    score = int((correct/total)*40)
    score_map = {
        40: 9,
        39: 8.5,
        37: 8,
        36: 7.5,
        34: 7,
        32: 6.5,
        30: 6,
        27: 5.5,
        23: 5,
        19: 4.5,
        15: 4,
        0: 0,
    }

    for map in score_map:
        if score >= map:
            return score_map[map]

    return 0.0


def evaluate_writing_attempt(attempt):
    openai.api_key = settings.OPENAI_SECRET
    prompt = "Please evaluate the following Writing Attempt"
    user_answers = attempt.answers
    evaluation = {}

    for answer in user_answers:
        section = attempt.module.sections.filter(id=int(answer)).first()
        task = section.task
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "user", "content": writing_prompts.PROMPT0},
                {"role": "user", "content": writing_prompts.PROMPT1},
                {"role": "user", "content": f'TASK: {task}'},
                {"role": "user",
                    "content": f'User Answer: {user_answers[answer]}'},
                {"role": "user", "content": writing_prompts.PROMPT2},
                {"role": "user", "content": writing_prompts.PROMPT3},
                {"role": "user", "content": writing_prompts.PROMPT4},
            ]
        )
        content = completion.choices[0].message['content']
        print(content)
        evaluation[answer] = content
    attempt.evaluation = evaluation
    return attempt
