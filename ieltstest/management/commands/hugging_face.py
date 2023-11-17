from django.core.management.base import BaseCommand
from ieltstest.models import SpeakingAttemptAudio
import whisper
from transformers import pipeline
from happytransformer import HappyTextToText, TTSettings

HUGGINGFACE_API = "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"


class Command(BaseCommand):
    help = 'Converts audio to text using speech recognition'

    def handle(self, *args, **kwargs):
        # text_generator()
        speech_recognization()


def text_generator():
    generator = pipeline("text-generation", model="distilgpt2")
    res = generator(
        """
Fix Grammar and spellings:
My name Kevin Valani, I am software developer, who likes develope code


        """,
        max_length=800,
        # num_return_sequences=2
    )

    print(res)


def grammar():
    happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")

    args = TTSettings(num_beams=15, min_length=10)

    # Add the prefix "grammar: " before each input
    result = happy_tt.generate_text(
        """
        The entertainment industry is one of the largest sectors in all around the world. Some think that the people who work in that industry earn too much money considering their bad influence on society, and I agree.  Others, however, believe that their positive impact on others is worth the money that they are paid.

On the one hand, there is no doubt that show business is an enormous and unfairly well paid sector. In addition to that, members of it do not add real value, compared to others like, for instance, education workers. Although in some countries teachers live with unreasonable wages, their responsibility, is extremely valuable for next generations become better people. Whereas a singer can earn double their yearly salary from one concert. The other important point is, for a balanced and equal society, the difference between income levels must not be very high. Regardless than their contribution, no one should make billions of dollars that easily, because that imbalance does have a significant negative impact on societies.

On the other hand, some people think that entertainers’ contribution to the modern life is worth the money they earn. It can be understood that for many people, watching a movie or going to a concert is irreplaceable with other activities; therefore, they think that their positive impact is crucial for a significant proportion of people. In addition to that, celebrities do compromise their privacy and freedom with being known by many others. In exchange of that, they do deserve a comfortable life with significantly better paychecks.

In conclusion, despite their minimal contribution with their work to the people and sacrifice from their private life; I believe that their impact is far from being positive and they are not paid fairly or balanced with others.
""", args=args)

    print(result.text)  # This sentence has bad grammar.


def speech_recognization():
    from transformers import pipeline

    transcriber = pipeline(model="openai/whisper-base")
    print(transcriber("https://huggingface.co/datasets/Narsil/asr_dummy/resolve/main/1.flac"))