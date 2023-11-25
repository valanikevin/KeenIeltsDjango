from django.db import models
from django.contrib.auth import get_user_model
from coachinginstitute.models import CoachingInstitute
from KeenIeltsDjango.models import SlugifiedBaseModal
from datetime import datetime, timedelta


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

    @property
    def average_score(self):
        from ieltstest.variables import get_individual_test_obj_serializer_from_slug, get_module_attempt_from_slug

        modules = ['reading', 'listening', 'writing', 'speaking']
        overall_scores = {}

        for module in modules:
            IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
                module)
            # Find average score of all attempts
            module_attempts = IndividualModuleAttempt.objects.filter(
                user=self.user, status="Evaluated")
            if module_attempts.exists():
                average_bands = module_attempts.aggregate(
                    models.Avg('bands'))['bands__avg']
                overall_scores[module] = round_to_half(average_bands)

        # Add overall average bands to overall_scores dict
        overall_scores['overall'] = round_to_half(sum(
            overall_scores.values())/len(overall_scores))

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
        last_fifteen_dates = [today - timedelta(days=i) for i in range(14, -1, -1)]

        # Initialize chart data for each module and each date
        for module in modules:
            IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(module)
            chart_data[module] = {date.strftime("%B %-d, %Y"): {'average_bands': None, 'attempt_count': 0} for date in last_fifteen_dates}

            for date in last_fifteen_dates:
                # Find average score of all attempts
                module_attempts = IndividualModuleAttempt.objects.filter(
                    user=self.user, status="Evaluated", created_at__date=date)
                if module_attempts.exists():
                    average_bands = module_attempts.aggregate(models.Avg('bands'))['bands__avg']
                    chart_data[module][date.strftime("%B %-d, %Y")]['average_bands'] = round_to_half(average_bands)
                    chart_data[module][date.strftime("%B %-d, %Y")]['attempt_count'] = module_attempts.count()

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
                chart_data['overall'][date.strftime("%B %-d, %Y")] = {'average_bands': round_to_half(overall_average_bands/module_count), 'attempt_count': total_attempts}
            else:
                chart_data['overall'][date.strftime("%B %-d, %Y")] = {'average_bands': None, 'attempt_count': 0}

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
        chart_format['dates'] = [date.strftime("%B %-d, %Y") for date in last_fifteen_dates]

        return chart_format



def round_to_half(number):
    rounded = round(number * 2) / 2

    # number should not be less than 1 and more than 9
    if rounded < 1:
        return 1
    elif rounded > 9:
        return 9
    else:
        return rounded
