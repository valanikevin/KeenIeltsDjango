from django.shortcuts import render
from ieltstest.variables import get_individual_test_obj_from_slug


def ieltstest(request):
    pass


def test_home(request, slug):
    IndividualTest = get_individual_test_obj_from_slug(slug)
    tests = IndividualTest.objects.filter(active=True)
    