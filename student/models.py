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
                overall_scores[module] = average_bands

        return overall_scores

    @property
    def fifteen_days_chart(self):
        from ieltstest.variables import get_individual_test_obj_serializer_from_slug, get_module_attempt_from_slug

        modules = ['listening', 'reading', 'writing', 'speaking']
        chart_data = {}

        # Get today's date
        today = datetime.now().date()

        # Generate a list of the last fifteen dates
        last_fifteen_dates = [today - timedelta(days=i) for i in range(15)]

        for module in modules:
            IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
                module)
            chart_data[module] = {}
            for date in last_fifteen_dates:
                # Find average score of all attempts
                module_attempts = IndividualModuleAttempt.objects.filter(
                    user=self.user, status="Evaluated", created_at__date=date)
                if module_attempts.exists():
                    average_bands = module_attempts.aggregate(
                        models.Avg('bands'))['bands__avg']
                    chart_data[module][date.strftime(
                        "%B %-d, %Y")] = average_bands

        return chart_data
