from rest_framework import serializers
from ieltstest.models import Book, ListeningModule, Test, ListeningSection


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


class ListeningTestHomeSerializer(serializers.Serializer):
    books = BookSerializer(many=True, read_only=True)
