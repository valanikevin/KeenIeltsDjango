from django.shortcuts import render
# from ieltstest.variables import get_individual_test_obj_serializer_from_slug
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ieltstest.serializers.listening_serializers import ListeningTestHomeSerializer
from ieltstest.models import Book


def ieltstest(request):
    pass


@api_view(['GET'])
def test_home(request, slug):
    books = Book.objects.all()
    serializer = ListeningTestHomeSerializer(
        {'books': books}, context={'request': request})
    return Response(serializer.data)
