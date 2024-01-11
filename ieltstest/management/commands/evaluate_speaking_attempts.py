from django.core.management.base import BaseCommand
from ieltstest.models import SpeakingAttempt
import whisper
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives


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
            attempt.status = 'Verify Bands'
            attempt.save()

            # Send email
            send_evaluation_email(attempt)
        print("Evaluted all speaking attempts")


def send_evaluation_email(attempt):
    message = f"""
Hi {attempt.user.first_name},
Your KeenIELTS speaking test result is now available on your account. To view your results, please log in to your account.

Test ID: {attempt.slug}
Book Name: {attempt.module.test.book.name}
Test Name: {attempt.module.test.name}

Regards,
Team KeenIELTS
"""

    # send_mail(
    #     subject='KeenIELTS Speaking Test Result',
    #     message=message,
    #     from_email='KeenIELTS <notifications@zepto.keenielts.com>',
    #     recipient_list=[attempt.user.email, ],
    #     fail_silently=True,
    # )

    return True