from rest_framework import serializers
from ieltstest.models import Book, ListeningModule, Test, ListeningSection


class ListeningSectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListeningSection
        fields = '__all__'


class ListeningModuleBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListeningModule
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    listening_module = ListeningModuleBasicSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    tests_with_listening_module = TestSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['created_at', 'slug', 'name', 'difficulty', 'cover',
                  'website', 'copyright', 'tests_with_listening_module']


class ListeningTestHomeSerializer(serializers.Serializer):
    books = BookSerializer(many=True, read_only=True)
