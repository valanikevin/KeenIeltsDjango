from django.shortcuts import render
from ieltstest.variables import get_individual_test_obj_serializer_from_slug
from rest_framework.decorators import api_view
from rest_framework.response import Response


def ieltstest(request):
    pass


@api_view(['GET'])
def test_home(request, slug):
    IndividualTest, IndividualTestSerializer = get_individual_test_obj_serializer_from_slug(
        slug)
    tests = IndividualTest.objects.order_by('-test__created_at')
    serializer = IndividualTestSerializer(tests, many=True)
    return Response(serializer.data)
