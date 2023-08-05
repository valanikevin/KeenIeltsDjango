
from ieltstest.models import ListeningModule, ListeningAttempt
from ieltstest.serializers.listening_serializers import ListeningModuleWithSectionSerializer


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
            attempt = test.get('attempt')
            return (obj, serializer, attempt)
    return None



