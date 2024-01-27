from django.core.management.base import BaseCommand
from ieltstest.models import SpeakingAttempt


class Command(BaseCommand):
    help = 'Evaluate speaking attempts and generate scores'

    def handle(self, *args, **kwargs):
        print("Evaluating all speaking attempts")
        attempts = SpeakingAttempt.objects.filter(
            internal_status='Completed', status='Completed')

        for attempt in attempts:
            print(f'Attempt: {attempt.slug}')
            # Evaluate Audio

            # Speech to text using Whisper
            attempt.audio_to_text()

            # Evaluate Audio using OpenAI
            attempt.get_evaluation()
            attempt.internal_status = 'Ready'
            attempt.status = 'Ready'
            attempt.save()

        print("Evaluted all speaking attempts")
