from rest_framework import serializers
from ieltstest.models import Book, ListeningModule, Test, ListeningSection, ListeningAttempt


class ListeningSectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListeningSection
        exclude = ['answers']


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


class BookSerializer(serializers.ModelSerializer):
    tests_with_listening_module = TestSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['created_at', 'slug', 'name', 'description', 'difficulty', 'cover',
                  'website', 'copyright', 'tests_with_listening_module']


class BookModuleSerializer(serializers.ModelSerializer):
    tests = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['created_at', 'slug', 'name', 'description', 'difficulty', 'cover',
                  'website', 'copyright', 'tests']

    def get_tests(self, obj):
        get_tests_function = {
            'listening': obj.tests_with_listening_module,
        }

        module_slug = self.context.get('module_slug')

        serializer = TestSerializer(
            get_tests_function.get(module_slug), many=True)

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
