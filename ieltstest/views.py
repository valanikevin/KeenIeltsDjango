from django.shortcuts import render
from ieltstest.variables import get_individual_test_obj_serializer_from_slug
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from ieltstest.serializers.listening_serializers import ListeningTestHomeSerializer
from ieltstest.models import Book
from rest_framework.permissions import IsAuthenticated


def ieltstest(request):
    pass


def get_books():
    books = Book.objects.order_by('-id')
    return books


@api_view(['GET'])
def module_home(request, slug):
    books = get_books()

    serializer = ListeningTestHomeSerializer(
        {'books': books}, context={'request': request})
    return Response(serializer.data)


@api_view(['OPTIONS'])
@permission_classes([IsAuthenticated])
def find_smart_test_from_book(request, module_type, book_slug):
    IndividualModule, IndividualModuleSerializer = get_individual_test_obj_serializer_from_slug(
        module_type)
    print(book_slug)
    tests = IndividualModule.objects.filter(
        test__book__slug=book_slug)

    # TODO: Filter test for user which he has never made attempt before.
    selected_test_slug = tests.order_by('?')

    if selected_test_slug.exists():
        selected_test_slug = selected_test_slug.first().slug
    else:
        return Response(status=500)
    return Response({'module_type': module_type, 'selected_module': selected_test_slug})


@api_view(['OPTIONS'])
@permission_classes([IsAuthenticated])
def get_module(request, module_type, module_slug):
    IndividualModule, IndividualModuleSerializer = get_individual_test_obj_serializer_from_slug(
        module_type)
    module = IndividualModule.objects.get(slug=module_slug)
    serializer = IndividualModuleSerializer(module, many=False)
    return Response(serializer.data)
