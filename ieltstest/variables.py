
from ieltstest.models import ListeningModule, ListeningAttempt, ReadingModule, ReadingAttempt, WritingModule, WritingAttempt, SpeakingModule, SpeakingAttempt, SpeakingSection
from ieltstest.serializers import ListeningModuleWithSectionSerializer, ListeningAttemptSerializer, ReadingModuleWithSectionSerializer, ReadingAttemptSerializer, WritingModuleWithSectionSerializer, WritingAttemptSerializer, SpeakingSectionSerializer, SpeakingAttemptSerializer, SpeakingModuleWithSectionSerializer


def get_individual_test_obj_serializer_from_slug(slug):
    tests = [
        {'slug': 'listening',
            'object': ListeningModule,
            'serializer': ListeningModuleWithSectionSerializer,
         },
        {'slug': 'reading',
            'object': ReadingModule,
            'serializer': ReadingModuleWithSectionSerializer,
         },
        {'slug': 'writing',
            'object': WritingModule,
            'serializer': WritingModuleWithSectionSerializer,
         },
        {'slug': 'speaking',
            'object': SpeakingModule,
            'serializer': SpeakingModuleWithSectionSerializer,
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
        'listening': (ListeningAttempt, ListeningAttemptSerializer),
        'reading': (ReadingAttempt, ReadingAttemptSerializer),
        'writing': (WritingAttempt, WritingAttemptSerializer),
        'speaking': (SpeakingAttempt, SpeakingAttemptSerializer),
    }

    return attempts.get(slug)
