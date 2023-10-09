from django.core.management.base import BaseCommand
from ieltstest.models import SpeakingAttemptAudio
import whisper


class Command(BaseCommand):
    help = 'Converts audio to text using speech recognition'

    def handle(self, *args, **kwargs):
        speaking_audio = SpeakingAttemptAudio.objects.first()
        audio_path = speaking_audio.audio.path
        print(f'AUDIO: {audio_path}')
        # Convert audio to WAV
        # replace "mp3" with the format of your file if different
        # audio = AudioSegment.from_file(audio_path, format="mp3")
        # audio = audio.set_channels(1)
        # audio = audio.set_frame_rate(16000)
        # wav_path = "temp.wav"
        # audio.export(wav_path, format="wav")
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path)
        print(result["text"])
