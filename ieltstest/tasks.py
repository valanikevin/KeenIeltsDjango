from __future__ import absolute_import, unicode_literals
from celery import shared_task
from ieltstest.models import SpeakingAttempt


@shared_task
def evaluate_speaking_attempts(slug=None):
    attempt = SpeakingAttempt.objects.get(slug=slug)
    print(f'Attempt: {attempt.slug}')
    # Evaluate Audio

    # Speech to text using Whisper
    attempt.audio_to_text()

    # Evaluate Audio using OpenAI
    attempt.get_evaluation()
    attempt.internal_status = 'Ready'
    attempt.status = 'Ready'
    attempt.save()

    print("Evaluted speaking attempt")