from rest_framework import serializers
from ieltstest.models import Book, ListeningTest, Test


class TestSerializer(serializers.ModelSerializer):
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
