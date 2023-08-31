from rest_framework import serializers
from ieltstest.models import Book, ListeningModule, Test, ListeningSection, ListeningAttempt, ReadingModule, ReadingSection, ReadingAttempt, WritingModule, WritingSection, WritingAttempt, SpeakingModule, SpeakingAttempt, SpeakingSection


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

    class Meta:
        model = SpeakingSection
        fields = '__all__'


class BookSerializerBasic(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = '__all__'


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
        url = f'http://localhost:8000{obj.audio.url}'
        return url


class ListeningModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListeningModule
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    listening_module = ListeningModuleSerializer(
        many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'


class BookModuleSerializer(serializers.ModelSerializer):
    tests = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['created_at', 'slug', 'name', 'description', 'difficulty', 'cover',
                  'website', 'copyright', 'tests']

    def get_tests(self, obj):
        module_slug = self.context.get('module_slug')
        user = self.context.get('user')
        if module_slug == 'listening':
            tests = obj.tests_with_listening_module
        elif module_slug == 'reading':
            tests = obj.tests_with_reading_module(user)
        elif module_slug == 'writing':
            tests = obj.tests_with_writing_module(user)
        elif module_slug == 'speaking':
            tests = obj.tests_with_speaking_module

        serializer = TestSerializer(
            tests, many=True)

        return serializer.data

    def get_cover(self, obj):
        return f'http://localhost:8000{obj.cover.url}'


class BookBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['slug', 'name', 'difficulty', 'cover']


class ListeningAttemptSerializer(serializers.ModelSerializer):
    book = serializers.SerializerMethodField()

    class Meta:
        model = ListeningAttempt
        fields = '__all__'

    def get_book(self, instance):
        return BookBasicSerializer(instance.module.test.book, many=False).data


class ReadingAttemptSerializer(serializers.ModelSerializer):
    book = serializers.SerializerMethodField()

    class Meta:
        model = ReadingAttempt
        fields = '__all__'

    def get_book(self, instance):
        return BookBasicSerializer(instance.module.test.book, many=False).data


class WritingAttemptSerializer(serializers.ModelSerializer):
    book = serializers.SerializerMethodField()

    class Meta:
        model = WritingAttempt
        fields = '__all__'

    def get_book(self, instance):
        return BookBasicSerializer(instance.module.test.book, many=False).data


class SpeakingAttemptSerializer(serializers.ModelSerializer):
    book = serializers.SerializerMethodField()

    class Meta:
        model = SpeakingAttempt
        fields = '__all__'

    def get_book(self, instance):
        return BookBasicSerializer(instance.module.test.book, many=False).data


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
