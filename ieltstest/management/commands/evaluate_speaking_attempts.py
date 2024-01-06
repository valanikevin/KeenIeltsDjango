from django.core.management.base import BaseCommand
from ieltstest.models import SpeakingAttempt
import whisper


class Command(BaseCommand):
    help = 'Evaluate speaking attempts and generate scores'

    def handle(self, *args, **kwargs):
        print("Evaluating all speaking attempts")
        attempts = SpeakingAttempt.objects.filter(status='Completed')
        
        for attempt in attempts:
            print(f'Attempt: {attempt.slug}')
            # Evaluate Audio

            # Speech to text using Whisper
            for audio in attempt.audios.all():
                audio.audio_to_text()

            # Evaluate Audio using OpenAI
            attempt.get_evaluation()
            attempt.status = 'Ready'
            attempt.save()

        print("Evaluted all speaking attempts")
