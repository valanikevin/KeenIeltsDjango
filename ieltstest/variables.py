
from ieltstest.models import ListeningModule, ListeningAttempt
from ieltstest.serializers import ListeningModuleWithSectionSerializer, ListeningAttemptSerializer


def get_individual_test_obj_serializer_from_slug(slug):
    tests = [
        {'slug': 'listening',
            'object': ListeningModule,
            'serializer': ListeningModuleWithSectionSerializer,
            'attempt': ListeningAttempt,
         }
    ]

    obj, serializer = None, None
    for test in tests:
        if test.get('slug') == slug:
            obj = test.get('object')
            serializer = test.get('serializer')

            return (obj, serializer)
    return None


def get_module_attempt_from_slug(slug):
    attempts = {
        'listening': (ListeningAttempt, ListeningAttemptSerializer)
    }

    return attempts.get(slug)
