from django.db import models
from django.contrib.auth import get_user_model
from coachinginstitute.models import CoachingInstitute
from KeenIeltsDjango.models import SlugifiedBaseModal, TimestampedBaseModel
from datetime import datetime, timedelta
from django.conf import settings
import os
from student.openai import dashboard_prompts
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from django.utils import timezone
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from django.core.cache import cache


class Student(SlugifiedBaseModal):
    TYPE = (
        ('academic', 'Academic'),
        ('general', 'General'),
    )
    user = models.OneToOneField(get_user_model(
    ), on_delete=models.CASCADE, help_text='Select base user for this student.')
    institute = models.ForeignKey(CoachingInstitute, on_delete=models.SET_NULL, null=True,
                                  blank=True, help_text="Is this student enrolled at any coaching institute?")
    type = models.CharField(
        choices=TYPE, help_text='What test type is student preparing for?', max_length=200, default='academic')

    bandsTarget = models.DecimalField(
        default=7.0, decimal_places=1, max_digits=2)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        # Flag to determine if the student instance is new
        is_new = self._state.adding

        # First save the Student instance
        super(Student, self).save(*args, **kwargs)

        # If this is a new instance, create OverallPerformanceFeedback
        if is_new:
            OverallPerformanceFeedback.objects.create(student=self)

    @property
    def recent_tests(self):
        from ieltstest.variables import get_individual_test_obj_serializer_from_slug, get_module_attempt_from_slug

        modules = ['reading', 'listening', 'writing', 'speaking']
        recent_tests = []

        for module in modules:
            IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
                module)

            # Find top 5 attempts from each module
            module_attempts = IndividualModuleAttempt.objects.filter(
                user=self.user, status="Evaluated").order_by('-created_at')[:5]
            if module_attempts.exists():
                for attempt in module_attempts:
                    recent_tests.append({
                        'created_at': attempt.created_at,
                        'module': module,
                        'score': attempt.bands,
                        'attempt_slug': attempt.slug,
                        'module_slug': attempt.module.slug,
                        'book_name': attempt.module.test.book.name,
                        'test_name': attempt.module.test.name,
                    })

        # Sort all attempts by created_at
        sorted_attempts = sorted(
            recent_tests, key=lambda x: x['created_at'], reverse=True)

        # Limit the number of items to a maximum of 10
        sorted_attempts = sorted_attempts[:15]

        return sorted_attempts

    @property
    def overall_feedback(self):
        if hasattr(self, 'overallperformancefeedback'):
            return self.overallperformancefeedback.feedback
        else:
            OverallPerformanceFeedback.objects.create(student=self)
            return self.overallperformancefeedback.feedback

    @property
    def average_score(self):
        from ieltstest.variables import get_individual_test_obj_serializer_from_slug, get_module_attempt_from_slug
        from django.db.models import Avg, Count

        modules = ['reading', 'listening', 'writing', 'speaking']
        overall_scores = {module: {'average_bands': 0,
                                   'attempt_count': 0} for module in modules}

        # Initialize 'overall' key with default values
        overall_scores['overall'] = {'average_bands': 0, 'total_attempts': 0}

        for module in modules:
            IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
                module)

            # Filter module attempts
            module_attempts = IndividualModuleAttempt.objects.filter(
                user=self.user, status="Evaluated")

            if module_attempts.exists():
                # Aggregate average bands and count of attempts
                aggregation_results = module_attempts.aggregate(
                    average_bands=Avg('bands'),
                    attempt_count=Count('id')
                )
                average_bands = aggregation_results['average_bands']
                attempt_count = aggregation_results['attempt_count']

                # Update average bands and attempt count
                overall_scores[module] = {
                    'average_bands': round_to_half(average_bands),
                    'attempt_count': attempt_count
                }

        # Calculate overall average bands and total attempts
        total_average = sum(d['average_bands'] for d in overall_scores.values(
        ) if 'average_bands' in d) / len(modules)
        total_attempts = sum(d['attempt_count']
                             for d in overall_scores.values() if 'attempt_count' in d)

        # Update overall scores
        overall_scores['overall'] = {
            'average_bands': round_to_half(total_average) if total_attempts > 0 else 0,
            'total_attempts': total_attempts
        }

        return overall_scores


# Function to round off a number to the nearest 0.5


    @property
    def fifteen_days_chart(self):
        from ieltstest.variables import get_individual_test_obj_serializer_from_slug, get_module_attempt_from_slug
        from django.db import models
        from datetime import datetime, timedelta

        modules = ['listening', 'reading', 'writing', 'speaking']
        chart_data = {}

        # Get today's date
        today = datetime.now().date()

        # Generate a list of the last fifteen dates
        last_fifteen_dates = [
            today - timedelta(days=i) for i in range(14, -1, -1)]

        # Initialize chart data for each module and each date
        for module in modules:
            IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
                module)
            chart_data[module] = {date.strftime(
                "%B %-d, %Y"): {'average_bands': 0, 'attempt_count': 0} for date in last_fifteen_dates}

            for date in last_fifteen_dates:
                # Find average score of all attempts
                module_attempts = IndividualModuleAttempt.objects.filter(
                    user=self.user, status="Evaluated", created_at__date=date)
                if module_attempts.exists():
                    average_bands = module_attempts.aggregate(
                        models.Avg('bands'))['bands__avg']
                    chart_data[module][date.strftime(
                        "%B %-d, %Y")]['average_bands'] = round_to_half(average_bands)
                    chart_data[module][date.strftime(
                        "%B %-d, %Y")]['attempt_count'] = module_attempts.count()

        # Add Overall Average Bands for the last fifteen days from chart_data of each module
        chart_data['overall'] = {}
        for date in last_fifteen_dates:
            overall_average_bands = 0
            total_attempts = 0
            module_count = 0
            for module in modules:
                module_data = chart_data[module][date.strftime("%B %-d, %Y")]
                if module_data['average_bands'] is not None:
                    overall_average_bands += module_data['average_bands']
                    total_attempts += module_data['attempt_count']
                    module_count += 1
            if module_count > 0:
                chart_data['overall'][date.strftime("%B %-d, %Y")] = {'average_bands': round_to_half(
                    overall_average_bands/module_count), 'attempt_count': total_attempts}
            else:
                chart_data['overall'][date.strftime(
                    "%B %-d, %Y")] = {'average_bands': 0.0, 'attempt_count': 0.0}

        # Prepare chart format with date labels and attempt counts
        chart_format = {
            module: {
                'average_bands': [data['average_bands'] for data in chart_data[module].values()],
                'attempt_count': [data['attempt_count'] for data in chart_data[module].values()]
            } for module in modules
        }
        chart_format['overall'] = {
            'average_bands': [data['average_bands'] for data in chart_data['overall'].values()],
            'attempt_count': [data['attempt_count'] for data in chart_data['overall'].values()]
        }
        chart_format['dates'] = [date.strftime(
            "%b. %-d") for date in last_fifteen_dates]

        return chart_format


def round_to_half(number):
    rounded = round(number * 2) / 2

    # number should not be less than 1 and more than 9
    if rounded < 1:
        rounded = 1
    elif rounded > 9:
        rounded = 9

    # Format the number to have one decimal point
    return float(format(rounded, '.1f'))


class OverallPerformanceFeedback(TimestampedBaseModel):
    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, help_text='Select student for this feedback.')
    raw_feedback = models.TextField(
        help_text='Write your feedback for this student.', blank=True, null=True)

    def __str__(self):
        return self.student.user.email

    @property
    def feedback(self):
        _feedback = ""
        if self.updated_at > timezone.now() - timedelta(days=1) and self.raw_feedback:
            _feedback = self.raw_feedback
        else:
            _feedback = openai_overall_feedback(self.student)
            self.raw_feedback = _feedback
            self.save()

        return process_openai_content(_feedback)


def process_openai_content(text):
    text = text.replace('\n', '<br />')
    return text


def openai_overall_feedback(student):
    OPENAI_KEY = settings.OPENAI_SECRET
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY
    chat_model = ChatOpenAI(
        temperature=1.0, model_name="gpt-3.5-turbo-16k")

    data = f"""
Student Name: {student.user.first_name}
Student Target: {student.bandsTarget}

Overall Performance Data:
{student.average_score}

Last 15 Days Performance Data:
{student.fifteen_days_chart}
"""
    prompt = dashboard_prompts.overall_feedback_prompt.format(data=data)

    messages = [SystemMessage(content=prompt)]
    evaluation = chat_model.invoke(messages).content

    return evaluation
