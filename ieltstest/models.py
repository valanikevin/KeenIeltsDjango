from django.db import models
from KeenIeltsDjango.models import SlugifiedBaseModal, TimestampedBaseModel, WeightedBaseModel
from coachinginstitute.models import CoachingInstitute
from ckeditor_uploader.fields import RichTextUploadingField
from ieltstest.answer_json.listening import get_listening_answer_default
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.core.files import File
import requests
from tempfile import NamedTemporaryFile
from ieltstest.openai import writing_prompts, speaking_prompts
import whisper
import os
import json
import time
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain
from django.core.files.base import ContentFile
from pydub import AudioSegment
from io import BytesIO

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
        ('Section 1', 'Section 1'),
        ('Section 2', 'Section 2'),
        ('Section 3', 'Section 3'),
        ('Section 4', 'Section 4'),
    )
    section = models.CharField(
        choices=SECTION, help_text='What is section type?')
    name = models.CharField(
        max_length=200, help_text='Test ideentifier name. e.g. Art and Science')

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

    @property
    def tests_with_speaking_module(self):
        tests = self.tests.filter(speakingmodule__test__isnull=False)
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
    total_questions = models.PositiveIntegerField(
        help_text='How many questions are there in this module?', default=0)

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
    total_questions = models.PositiveIntegerField(
        help_text='How many questions are there in this section?', default=0)
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

    @property
    def bands_description(self):
        if self.bands:
            return ielts_listening_bands_description.get(self.bands)
        else:
            return None


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

    @property
    def bands_description(self):
        if self.bands:
            return ielts_reading_bands_description.get(self.bands)
        else:
            return None


class ReadingModule(IndividualModuleAbstract):
    total_questions = models.PositiveIntegerField(
        help_text='How many questions are there in this module?', default=0)

    def __str__(self):
        return self.test.name if self.test else ""

    def save(self, *args, **kwargs):
        update_form_fields_with_ids(self)
        super(ReadingModule, self).save(*args, **kwargs)

    @property
    def sections(self):
        return ReadingSection.objects.filter(reading_module=self).order_by('section')


class ReadingSection(IndividualModuleSectionAbstract):
    total_questions = models.PositiveIntegerField(
        help_text='How many questions are there in this section?', default=0)
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
    SECTION = (
        ('Task 1', 'Task 1'),
        ('Task 2', 'Task 2'),
    )
    section = models.CharField(
        choices=SECTION, help_text='What is section type?')
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
    evaluation = models.TextField(
        null=True, blank=True, help_text='Evaluation Task 1 for this attempt')
    evaluation_2 = models.TextField(
        null=True, blank=True, help_text='Evaluation Task 2 for this attempt')

    def save(self, *args, **kwargs):
        bands = 0.0
        tasks = 0
        if self.evaluation:
            bands += evalution_json(self.evaluation).get('overall_band_score', 0.0)
            tasks += 1
        if self.evaluation_2:
            bands += evalution_json(self.evaluation_2).get(
                'overall_band_score', 0.0)
            tasks += 1

        # Calculate average if tasks > 0 to avoid division by zero
        average_band = bands / tasks if tasks > 0 else 0.0

        # Round the average_band as per IELTS rounding rules
        fraction = average_band % 1
        if fraction < 0.25:
            rounded_band = int(average_band)
        elif fraction < 0.75:
            rounded_band = int(average_band) + 0.5
        else:
            rounded_band = int(average_band) + 1

        self.bands = rounded_band

        return super(WritingAttempt, self).save(*args, **kwargs)

    @property
    def bands_description(self):
        if self.bands:
            return ielts_writing_bands_description.get(self.bands)
        else:
            return None

    def get_evaluation(self, section):
        if section.section == "Task 1" and self.evaluation:
            return evalution_json(self.evaluation)
        elif section.section == "Task 2" and self.evaluation_2:
            return evalution_json(self.evaluation_2)

        evaluation = openai_get_writing_evaluation(self, section)

        if section.section == "Task 1":
            self.evaluation = evaluation
        elif section.section == "Task 2":
            self.evaluation_2 = evaluation

        self.save()

        if section.section == "Task 1" and self.evaluation:
            return evalution_json(self.evaluation)
        elif section.section == "Task 2" and self.evaluation_2:
            return evalution_json(self.evaluation_2)

        return {}


class SpeakingModule(IndividualModuleAbstract):
    def __str__(self):
        return self.test.name if self.test else ""

    @property
    def sections(self):
        return SpeakingSection.objects.filter(speaking_module=self).order_by('section')


class SpeakingSection(IndividualModuleSectionAbstract):
    SECTION = (
        ('Part 1', 'Part 1'),
        ('Part 2', 'Part 2'),
        ('Part 3', 'Part 3'),
    )
    section = models.CharField(
        choices=SECTION, help_text='What is section type?')
    question_type = models.ForeignKey(
        QuestionType, on_delete=models.CASCADE, help_text='Choose question type for this section', null=True)
    speaking_module = models.ForeignKey(
        SpeakingModule, on_delete=models.CASCADE, help_text='Select parent writing module')

    def __str__(self):
        return self.name

    @property
    def questions(self):
        return SpeakingSectionQuestion.objects.filter(speaking_section=self).order_by('weight')


class SpeakingSectionQuestion(WeightedBaseModel):
    speaking_section = models.ForeignKey(
        SpeakingSection, on_delete=models.CASCADE, help_text='Select parent speaking section')
    question = models.CharField(
        max_length=300, help_text='Add speaking section question.')
    help_text = models.TextField(
        help_text='Add helper text for this question', null=True, blank=True)

    def __str__(self):
        return self.question


class SpeakingAttempt(IndividualModuleAttemptAbstract):
    module = models.ForeignKey(
        'SpeakingModule', help_text='Select Parent module for this attempt', on_delete=models.CASCADE)
    merged_audio = models.FileField(
        help_text="Merged Audio File from all the audios", null=True, blank=True)

    def save(self, *args, **kwargs):
        evaluation = self.evaluation_json

        if not self.merged_audio:
            self = merge_speaking_audio(self)

        if evaluation:
            self.bands = evaluation.get('overall_band_score')

        # Save again to ensure the FileField and other fields are updated
        super(SpeakingAttempt, self).save(*args, **kwargs)

    @property
    def bands_description(self):
        if self.bands:
            return ielts_speaking_bands_description.get(self.bands)
        else:
            return None

    def get_evaluation(self):

        if self.evaluation:
            return self.evaluation_json

        # Generate OpenAI Evaluation
        evaluation = openai_get_speaking_evaluation(self)

        self.evaluation = str(evaluation)
        self.save()

        # Return Evaluation
        return self.evaluation_json_section()

    @property
    def evaluation_json(self):
        try:
            return eval(str(self.evaluation))
        except Exception as e:
            print(e)
            return None

    def evaluation_json_section(self):
        return eval(str(self.evaluation_json))

    @property
    def audios(self):
        return SpeakingAttemptAudio.objects.filter(
            attempt=self).order_by('section__section')


def merge_speaking_audio(instance):
    print("Merging Audio")

    # Initialize an empty AudioSegment object
    merged_audio = AudioSegment.empty()

    # Assuming 'audios' is a queryset
    for audio in instance.audios.all():
        audio_segment = AudioSegment.from_file(audio.audio.path)

        # Concatenate audio
        merged_audio += audio_segment

    # Create in-memory byte buffer
    buffer = BytesIO()
    merged_audio.export(buffer, format='mp3')
    buffer.seek(0)  # Rewind the buffer

    # Create a Django ContentFile and save to the FileField
    content_file = ContentFile(buffer.read(), 'merged_file.mp3')
    instance.merged_audio = content_file

    buffer.close()  # Close the buffer

    return instance


class SpeakingAttemptAudio(models.Model):
    attempt = models.ForeignKey(
        SpeakingAttempt, help_text='Select attempt for this audio', on_delete=models.CASCADE)
    section = models.ForeignKey(
        SpeakingSection, on_delete=models.CASCADE, help_text='Select parent speaking section')
    audio = models.FileField(
        help_text='Add Audio file for the speaking attempt')
    audio_text = models.TextField(
        null=True, blank=True, help_text='Text converted from the original audio')
    timestamps = models.JSONField(
        null=True, help_text='Timestamps for each question in the audio', blank=True)

    def __str__(self):
        return self.attempt.slug

    @property
    def audio_to_text(self):
        if not self.audio_text:
            model = whisper.load_model("tiny")
            result = model.transcribe(self.audio.path)
            self.audio_text = result["text"]
            self.save()
        return self.audio_text


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
        0: 1,
    }

    for map in score_map:
        if score >= map:
            return score_map[map]

    return 1.0


def get_reading_academic_ielts_score(correct, total=40):
    score = int((correct/total)*40)
    score_map = {
        39: 9.0,
        37: 8.5,
        35: 8.0,
        33: 7.5,
        30: 7.0,
        27: 6.5,
        23: 6.0,
        19: 5.5,
        15: 5.0,
        13: 4.5,
        10: 4.0,
        0: 1.0,
    }

    for map in score_map:
        if score >= map:
            return score_map[map]

    return 1.0


def get_reading_general_ielts_score(correct, total=40):
    score = int((correct/total)*40)
    score_map = {
        40: 9.0,
        39: 8.5,
        37: 8.0,
        36: 7.5,
        34: 7.0,
        32: 6.5,
        30: 6.0,
        27: 5.5,
        23: 5.0,
        19: 4.5,
        15: 4.0,
        0: 0.0,
    }

    for map in score_map:
        if score >= map:
            return score_map[map]

    return 0.0


def extract_between(text, start, end):
    import re
    pattern = f"{re.escape(start)}(.*?){re.escape(end)}"
    matches = re.search(pattern, text, re.DOTALL)

    if matches:
        return matches.group(1)
    else:
        return None


def process_writing_content(text):
    text = text.replace('\n', '</br>')
    return text


def openai_get_speaking_evaluation(attempt):
    OPENAI_KEY = settings.OPENAI_SECRET
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY

    data = ""
    for audio in attempt.audios:
        question_list = [
            question.question for question in audio.section.questions]

        data = data + f"""
IELTS Speaking Part: {audio.section.section},
Questions Asked: {question_list},
Test Taker Audio Transcript: {audio.audio_to_text}\n\n
"""

    prompt = PromptTemplate(template=speaking_prompts.speaking_evaluation_prompt, input_variables=[
                            "data"])

    llm = LLMChain(llm=OpenAI(model_name="gpt-3.5-turbo-16k",
                   temperature=0.6), prompt=prompt)

    evaluation = llm.predict(data=data)
    return evaluation


def get_writing_empty_evaluation():
    evaluation = {
        "overall_band_score": 1.0,
        "task_achievement_band_score": 1.0,
        "coherence_and_cohesion_band_score": 1.0,
        "lexical_resource_band_score": 1.0,
        "grammatical_range_accuracy_band_score": 1.0,
        "overall_personalized_feedback_suggestions": "It appears your response was too brief for a detailed evaluation in this task. Please attempt the exam again, ensuring you meet the required word count for accurate results.",
        "vocabulary_choice_suggestions": [
            "The response lacks adequate word count, so no vocabulary suggestions can be provided at this time.",
        ]
    }

    return evaluation


def openai_get_writing_evaluation(attempt, section):
    OPENAI_KEY = settings.OPENAI_SECRET
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY

    answer = attempt.answers.get(str(section.id))
    word_count = len(answer.split())

    if word_count < 70:
        return get_writing_empty_evaluation()

    prompt = PromptTemplate(template=writing_prompts.writing_evaluation_prompt, input_variables=[
                            "task", "question", "answer"])
    llm = LLMChain(llm=OpenAI(model_name="gpt-3.5-turbo-16k",
                   temperature=0.6), prompt=prompt, verbose=True)
    evaluation = llm.predict(task=section.section,
                             question=section.questions, answer=answer)
    return evaluation


def evalution_json(data):
    try:
        evaluation = eval(str(data))
        return evaluation
    except Exception as e:
        print(e)
        return {}


ielts_writing_bands_description = {
    1.0: "You have no ability to use the language except for a few isolated words.",
    1.5: "You can understand and convey very basic information if it's repeated slowly and clearly.",
    2.0: "You have great difficulty understanding written English.",
    2.5: "You can convey basic information about yourself and your immediate surroundings.",
    3.0: "You can convey and understand only the general meaning in very familiar situations.",
    3.5: "You can write short, simple sentences on familiar topics, but errors are frequent.",
    4.0: "You have a basic competency in writing but make frequent errors and misunderstandings.",
    4.5: "You can convey familiar information and ideas adequately, but struggle with unfamiliar topics.",
    5.0: "You can communicate basic ideas related to familiar topics but have difficulty with complex language.",
    5.5: "You generally have a good grasp of the language but may make occasional errors or show signs of hesitation.",
    6.0: "You can write at a competent level, effectively conveying ideas but might lack in complex sentence structures.",
    6.5: "You have a good command of the language, though there might be occasional inaccuracies and misunderstandings in some situations.",
    7.0: "You have a strong command of the language and can produce complex sentences with few errors.",
    7.5: "You show a high level of proficiency in writing, with only occasional inaccuracies.",
    8.0: "You write very fluently and accurately, effectively using complex language structures.",
    8.5: "You have a near-perfect command of the language, with only rare inaccuracies.",
    9.0: "You demonstrate full mastery over the language and write with complete accuracy."
}


ielts_speaking_bands_description = {
    1.0: "You can only use isolated words and cannot communicate meaningfully in English.",
    1.5: "You can understand and convey very basic information if spoken slowly and clearly.",
    2.0: "You struggle significantly with understanding and expressing yourself in English.",
    2.5: "You can communicate about basic needs and personal experiences, though with many errors and pauses.",
    3.0: "You can convey and understand general meaning in familiar situations but often struggle with communication.",
    3.5: "You can handle basic communication in your field, but with frequent misunderstandings.",
    4.0: "You are able to discuss familiar topics but often face difficulty with complex ideas or unfamiliar topics.",
    4.5: "You can communicate about familiar topics with relative ease, but struggle with abstract or complex discussions.",
    5.0: "You can engage in generally effective communication, but may often misunderstand nuances or struggle with unfamiliar topics.",
    5.5: "You can handle a variety of communication tasks effectively, but sometimes inaccuracies and misunderstandings occur.",
    6.0: "You can communicate effectively in most situations, but occasional errors and misunderstandings can still occur.",
    6.5: "You speak the language well and can participate in a variety of conversations, but may still have occasional difficulties or inaccuracies.",
    7.0: "You have a good command of the language and can handle complex interactions and discussions, with occasional lapses in understanding or expression.",
    7.5: "You are able to participate in complex discussions and express yourself clearly and naturally, with only occasional inaccuracies.",
    8.0: "You speak fluently and accurately and can handle all kinds of communication situations, with only rare misunderstandings.",
    8.5: "You have a full command of the language with almost perfect fluency, clarity, and coherence.",
    9.0: "You have expert command of the language and can speak with precision, fluency, and sophistication."
}

ielts_listening_bands_description = {
    1.0: "You find it extremely difficult to understand any spoken English.",
    1.5: "You can catch occasional words or phrases, but understanding spoken content is largely challenging.",
    2.0: "You struggle to grasp the main points of clear and slow speech, even in very familiar contexts.",
    2.5: "You can understand basic information and short conversations if spoken slowly and clearly.",
    3.0: "You can catch the general meaning of slow and clear speech on familiar topics but often miss details.",
    3.5: "You can understand the main ideas of clear speech on familiar topics but may get lost in complex or rapid speech.",
    4.0: "You can follow most conversations and audio content on familiar subjects, though some phrases or idioms may be challenging.",
    4.5: "You can understand straightforward factual information and follow conversations, but may struggle with complex ideas or unfamiliar contexts.",
    5.0: "You can catch the main ideas in most audio content, but may miss some details or nuanced points.",
    5.5: "You can understand a variety of audio content, from news to conversations, but might face difficulty with rapid or accented speech.",
    6.0: "You have a competent understanding of spoken English in many contexts, but occasionally might miss details in complex or unfamiliar situations.",
    6.5: "You can understand detailed language and recognize implicit meaning in various contexts, though some challenging situations might still pose difficulties.",
    7.0: "You have a good command over understanding spoken English in diverse situations, including recognizing speaker opinions and attitudes.",
    7.5: "You can handle a wide range of listening activities, from lectures to discussions, understanding detailed reasoning and implicit meaning.",
    8.0: "You have a very good understanding of lengthy speeches, recognizing contradictions, and differentiating between facts and opinions.",
    8.5: "You can comprehend virtually everything you hear, regardless of topic or speaker, with only occasional need for clarification.",
    9.0: "You have an expert level of listening comprehension, understanding everything in both concrete and abstract contexts, even when faced with complex language."
}

ielts_reading_bands_description = {
    1.0: "You have extreme difficulty understanding written English.",
    1.5: "You can identify very basic words or phrases, but grasping meaning from sentences or paragraphs is challenging.",
    2.0: "You can pick out familiar names and phrases but struggle to understand the main idea of the content.",
    2.5: "You can understand basic information and short texts if they are related to familiar topics.",
    3.0: "You can comprehend the general meaning of short texts but often miss details or specific information.",
    3.5: "You can read and understand texts related to familiar topics but might struggle with more complex language or unfamiliar contexts.",
    4.0: "You can understand most of the content you read, especially if it's on familiar subjects, but idiomatic or specialized language may be challenging.",
    4.5: "You can understand texts that deal with everyday topics and can grasp the main idea of more complex content, but may miss some details.",
    5.0: "You can comprehend texts from a variety of sources, but might face difficulty with abstract concepts or detailed arguments.",
    5.5: "You have a solid grasp of the language, understanding main ideas and details in most texts, but complex or unfamiliar topics may pose challenges.",
    6.0: "You can understand complex language and detailed reasoning in texts, though occasionally might miss nuanced points or implicit meanings.",
    6.5: "You can read and interpret a wide range of texts, recognizing the writer's opinions, attitudes, and purposes, even if the topic is unfamiliar.",
    7.0: "You have a good command of reading comprehension, understanding detailed information, and recognizing implicit meaning in various contexts.",
    7.5: "You can handle a broad range of complex texts, understanding detailed reasoning, and distinguishing between facts and opinions.",
    8.0: "You have a very good command of reading comprehension, understanding contradictions, and fully grasping content even when it deals with abstract concepts.",
    8.5: "You can comprehend virtually everything you read, from complex articles to abstract writings, with a deep understanding of structure and meaning.",
    9.0: "You have an expert level of reading comprehension, understanding everything in both concrete and abstract contexts, even when faced with complex language."
}
