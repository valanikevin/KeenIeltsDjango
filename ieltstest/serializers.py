from rest_framework import serializers
from ieltstest.models import Book, ListeningModule, Test, ListeningSection


class ListeningSectionAllFieldsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListeningSection
        fields = '__all__'


class ListeningSectionBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListeningSection
        fields = ['id', 'section', 'name', ]


class ListeningModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningModule
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    listening_module = ListeningModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    tests = TestSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = '__all__'


class ListeningTestHomeSerializer(serializers.Serializer):
    books = BookSerializer(many=True, read_only=True)
