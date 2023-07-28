from django.shortcuts import render
# from ieltstest.variables import get_individual_test_obj_serializer_from_slug
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ieltstest.serializers.listening_serializers import ListeningTestHomeSerializer
from ieltstest.models import Book


def ieltstest(request):
    pass


def books_with_listening_module():
    books = Book.objects.order_by('-id')
    books_id = []
    for book in books:
        if book.tests_with_listening_module.exists():
            books_id .append(book.id)

    books = books.filter(pk__in=books_id)
    return books


@api_view(['GET'])
def test_home(request, slug):
    books = books_with_listening_module()
    print(books)
    serializer = ListeningTestHomeSerializer(
        {'books': books}, context={'request': request})
    return Response(serializer.data)
