
from ieltstest.models import ListeningTest


def get_individual_test_obj_from_slug(slug):
    tests = {
        'listening': ListeningTest,
    }

    return tests.get(slug)
