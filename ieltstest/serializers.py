from rest_framework import serializers
from ieltstest.models import Book, ListeningModule, Test, ListeningSection, ListeningAttempt, ReadingModule, ReadingSection, ReadingAttempt, WritingModule, WritingSection, WritingAttempt, SpeakingModule, SpeakingAttempt, SpeakingSection, SpeakingSectionQuestion, QuestionType, SpeakingAttemptAudio, FullTestAttempt, CoachingInstitute
from django.conf import settings
from KeenIeltsDjango.utils import imgix_url


class CoachingInstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachingInstitute
        fields = '__all__'


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = '__all__'


class SpeakingSectionQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeakingSectionQuestion
        fields = '__all__'


class ListeningSectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListeningSection
        exclude = ['answers']


class ReadingSectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReadingSection
        exclude = ['answers']


class WritingSectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = WritingSection
        fields = '__all__'


class SpeakingSectionSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    question_type = QuestionTypeSerializer(many=False, read_only=True)

    class Meta:
        model = SpeakingSection
        fields = '__all__'

    def get_questions(self, obj):
        serializer = SpeakingSectionQuestionSerializer(
            obj.questions, many=True, read_only=True)
        return serializer.data


class BookSerializerBasic(serializers.ModelSerializer):
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__'

    def get_cover(self, obj):
        test_type = self.context.get('test_type')
        return f'{imgix_url(obj.cover(test_type=test_type).url)}'


class TestWithBookSerializer(serializers.ModelSerializer):
    book = BookSerializerBasic(many=False, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'


class ListeningModuleWithSectionSerializer(serializers.ModelSerializer):
    sections = ListeningSectionSerializer(many=True, read_only=True)
    test = TestWithBookSerializer(many=False, read_only=True)
    audio = serializers.SerializerMethodField()

    class Meta:
        model = ListeningModule
        fields = '__all__'

    def get_audio(self, obj):
        url = f'{imgix_url(obj.audio.url)}'
        return url


class ListeningModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListeningModule
        fields = '__all__'


class ReadingModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReadingModule
        fields = '__all__'


class WritingModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = WritingModule
        fields = '__all__'


class SpeakingModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpeakingModule
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    listening_module = ListeningModuleSerializer(
        many=True, read_only=True)
    reading_module = ReadingModuleSerializer(many=True, read_only=True)
    writing_module = WritingModuleSerializer(many=True, read_only=True)
    speaking_module = SpeakingModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'


class GetBookSerializer(serializers.ModelSerializer):
    tests = TestSerializer(many=True, read_only=True)
    cover = serializers.SerializerMethodField()
    institute = CoachingInstituteSerializer(many=False, read_only=True)

    class Meta:
        model = Book
        fields = ['created_at', 'slug', 'name', 'description', 'difficulty', 'cover',
                  'website', 'copyright', 'tests', 'institute']

    def get_cover(self, obj):
        test_type = self.context.get('test_type')
        return f'{imgix_url(obj.cover(test_type=test_type).url)}'


class BookModuleSerializer(serializers.ModelSerializer):
    tests = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['created_at', 'slug', 'name', 'description', 'difficulty', 'cover',
                  'website', 'copyright', 'tests']

    def get_tests(self, obj):
        module_slug = self.context.get('module_slug')
        test_type = self.context.get('test_type')
        if module_slug == 'listening':
            tests = obj.tests_with_listening_module
        elif module_slug == 'reading':
            tests = obj.tests_with_reading_module(test_type)
        elif module_slug == 'writing':
            tests = obj.tests_with_writing_module(test_type)
        elif module_slug == 'speaking':
            tests = obj.tests_with_speaking_module
        elif module_slug == 'fulltest':
            tests = obj.tests_with_all_module(test_type)

        serializer = TestSerializer(
            tests, many=True)

        return serializer.data

    def get_cover(self, obj):
        test_type = self.context.get('test_type')
        return f'{imgix_url(obj.cover(test_type=test_type).url)}'


class BookBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['slug', 'name', 'difficulty', 'cover']


class AttemptSerializer(serializers.ModelSerializer):

    book = serializers.SerializerMethodField()
    bands_description = serializers.SerializerMethodField()
    full_test_attempt_slug = serializers.SerializerMethodField()
    full_test_next_attempt = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_book(self, instance):
        return BookBasicSerializer(instance.module.test.book, many=False).data

    def get_bands_description(self, instance):
        return instance.bands_description

    def get_full_test_attempt_slug(self, instance):
        return full_test_attempt_slug(instance)

    def get_full_test_next_attempt(self, instance):
        return full_test_next_attempt(instance)


class ListeningAttemptSerializer(AttemptSerializer):
    book = serializers.SerializerMethodField()
    bands_description = serializers.SerializerMethodField()

    class Meta:
        model = ListeningAttempt
        fields = '__all__'


class ReadingAttemptSerializer(AttemptSerializer):

    class Meta:
        model = ReadingAttempt
        fields = '__all__'


class WritingAttemptSerializer(AttemptSerializer):
    full_test_attempt_slug = serializers.SerializerMethodField()
    full_test_next_attempt = serializers.SerializerMethodField()

    class Meta:
        model = WritingAttempt
        fields = '__all__'


class SpeakingAttemptAudioSerializer(serializers.ModelSerializer):
    audio = serializers.SerializerMethodField()

    def get_audio(self, obj):
        url = f'{imgix_url(obj.audio.url)}'
        return url

    class Meta:
        model = SpeakingAttemptAudio
        fields = '__all__'


class SpeakingAttemptSerializer(AttemptSerializer):
    audios = SpeakingAttemptAudioSerializer(many=True, read_only=True)
    merged_audio = serializers.SerializerMethodField()

    def get_merged_audio(self, obj):
        url = f'{imgix_url(obj.merged_audio.url)}' if obj.merged_audio else None
        return url

    class Meta:
        model = SpeakingAttempt
        fields = '__all__'


class ReadingModuleWithSectionSerializer(serializers.ModelSerializer):
    sections = ReadingSectionSerializer(many=True, read_only=True)
    test = TestWithBookSerializer(many=False, read_only=True)

    class Meta:
        model = ReadingModule
        fields = '__all__'


class WritingModuleWithSectionSerializer(serializers.ModelSerializer):
    sections = WritingSectionSerializer(many=True, read_only=True)
    test = TestWithBookSerializer(many=False, read_only=True)

    class Meta:
        model = WritingModule
        fields = '__all__'


class SpeakingModuleWithSectionSerializer(serializers.ModelSerializer):
    sections = SpeakingSectionSerializer(many=True, read_only=True)
    test = TestWithBookSerializer(many=False, read_only=True)

    class Meta:
        model = SpeakingModule
        fields = '__all__'


AttemptBasicList = ['id', 'slug', 'module_slug', 'status', 'created_at',
                    'updated_at', 'bands', 'bands_description']


class BaseAttemptSerializer(serializers.ModelSerializer):
    module_slug = serializers.SerializerMethodField()
    bands_description = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_bands_description(self, instance):
        return instance.bands_description

    def get_module_slug(self, instance):
        return instance.module.slug

    class Meta:
        fields = AttemptBasicList + ['bands_description']


class ListeningAttemptBasic(BaseAttemptSerializer):

    class Meta(BaseAttemptSerializer.Meta):
        model = ListeningAttempt


class ReadingAttemptBasic(BaseAttemptSerializer):

    class Meta(BaseAttemptSerializer.Meta):
        model = ReadingAttempt


class WritingAttemptBasic(BaseAttemptSerializer):

    class Meta(BaseAttemptSerializer.Meta):
        model = WritingAttempt


class SpeakingAttemptBasic(BaseAttemptSerializer):

    class Meta(BaseAttemptSerializer.Meta):
        model = SpeakingAttempt


class FullTestAttemptSerializer(serializers.ModelSerializer):
    test = TestWithBookSerializer(many=False, read_only=True)
    listening_attempt = ListeningAttemptBasic(many=False, read_only=True)
    reading_attempt = ReadingAttemptBasic(many=False, read_only=True)
    writing_attempt = WritingAttemptBasic(many=False, read_only=True)
    speaking_attempt = SpeakingAttemptBasic(many=False, read_only=True)

    class Meta:
        model = FullTestAttempt
        fields = '__all__'

    def get_book(self, instance):
        return BookBasicSerializer(instance.test.book, many=False).data


def full_test_attempt_slug(instance):
    try:
        item = instance.fulltestattempt.slug if instance.fulltestattempt else None
    except Exception as e:
        item = None
    return item


def full_test_next_attempt(instance):
    try:
        attempt_data = instance.fulltestattempt.next_module_attempt if instance.fulltestattempt else None
    except Exception as e:
        attempt_data = None

    return attempt_data
