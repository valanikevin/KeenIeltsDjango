from rest_framework import serializers
from ieltstest.models import Book, ListeningTest, Test


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'


class ListeningTestSerializer(serializers.ModelSerializer):
    test = TestSerializer(many=False, read_only=True)

    class Meta:
        model = ListeningTest
        fields = '__all__'
