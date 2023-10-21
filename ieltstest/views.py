from django.shortcuts import render
from ieltstest.variables import get_individual_test_obj_serializer_from_slug, get_module_attempt_from_slug
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from ieltstest.serializers import BookModuleSerializer
from ieltstest.models import Book, SpeakingAttemptAudio, WritingAttempt, SpeakingSection, SpeakingAttempt, WritingSection
from rest_framework.permissions import IsAuthenticated
import json
import re
import openai
from django.conf import settings
from ieltstest.openai import writing_prompts
from django.core import serializers
from django.core.files.base import ContentFile


def ieltstest(request):
    pass


def get_books():
    books = Book.objects.order_by('-id')
    return books


@api_view(['GET'])
def module_home(request, slug):
    print(f'MODULE: {slug}')
    books = get_books()
    serializer = BookModuleSerializer(
        books, context={'module_slug': slug, 'user': request.user}, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_smart_test_from_book(request, module_type, book_slug):
    IndividualModule, IndividualModuleSerializer = get_individual_test_obj_serializer_from_slug(
        module_type)

    IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
        module_type)

    modules = IndividualModule.objects.filter(
        test__book__slug=book_slug)

    specific_test = request.POST.get('specific_test')

    if specific_test:
        selected_module = modules.filter(test__slug=specific_test)
    else:
        # TODO: Filter test for user which he has never made attempt before.
        selected_module = modules.order_by('?')

    if selected_module.exists():
        selected_module = selected_module.first()
        attempt = IndividualModuleAttempt.objects.create(
            user=request.user, module=selected_module)
    else:
        return Response(status=500)
    return Response({'module_type': module_type, 'selected_module': selected_module.slug, 'attempt': attempt.slug})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_module(request, module_type, module_slug):
    IndividualModule, IndividualModuleSerializer = get_individual_test_obj_serializer_from_slug(
        module_type)
    module = IndividualModule.objects.get(slug=module_slug)
    serializer = IndividualModuleSerializer(module, many=False)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_attempt(request, module_type, attempt_slug):
    IndividualModule, IndividualModuleSerializer = get_individual_test_obj_serializer_from_slug(
        module_type)
    IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
        module_type)
    attempt = IndividualModuleAttempt.objects.get(slug=attempt_slug)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    answers = body.get('answers')
    attempt_type = body.get('attempt_type')

    attempt.answers = answers
    attempt.status = attempt_type
    attempt.save()

    data = {
        'status': attempt.status,
    }

    return Response(data=data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_attempt_speaking(request, attempt_slug, module_type='speaking'):
    # Get your models and serializers (this part is based on your existing code)
    IndividualModule, IndividualModuleSerializer = get_individual_test_obj_serializer_from_slug(
        module_type)
    IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
        module_type)

    # Get the attempt object
    attempt = IndividualModuleAttempt.objects.get(slug=attempt_slug)

    timestamps = {}

    # Parsing other POST Data (excluding audio)
    for key, value in request.POST.items():
        if key != 'attempt_type':
            main_key, nested_key = key.split(',')
            main_key = int(main_key)
            nested_key = int(nested_key)

            nested_value = json.loads(value)

            if main_key not in timestamps:
                timestamps[main_key] = {}

            timestamps[main_key][nested_key] = nested_value

    # Loop through each file and save it
    for section_id, audio_blob in request.FILES.items():
        # I'm assuming section_id is the same as the 'key' you used in FormData
        section = SpeakingSection.objects.get(id=int(section_id))

        # Create or update the audio for this section
        speaking_audio, created = SpeakingAttemptAudio.objects.update_or_create(
            section=section,
            attempt=attempt,
            defaults={'timestamps': timestamps.get(int(section_id))}
        )

        # Save the audio blob as a file
        speaking_audio.audio.save(
            f'{section_id}.mp3', ContentFile(audio_blob.read()))

    attempt_type = request.POST.get('attempt_type')
    attempt.status = attempt_type
    attempt.save()

    data = {
        'status': attempt.status,
    }

    return Response(data=data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_attempt(request, module_type, attempt_slug):
    IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
        module_type)
    attempt = IndividualModuleAttempt.objects.get(slug=attempt_slug)
    serializer = IndividualModuleAttemptSerializer(attempt,  many=False)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_writing_evaluation(request, attempt_slug, section_id):
    attempt = WritingAttempt.objects.get(slug=attempt_slug)
    section = WritingSection.objects.get(id=section_id)
    evaluation = eval(attempt.get_evaluation(section=section))
    return Response(evaluation)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_speaking_evaluation(request, attempt_slug):
    attempt = SpeakingAttempt.objects.get(slug=attempt_slug)

    return Response(attempt.get_evaluation())


def openai_get_writing_bands(attempt):
    openai.api_key = settings.OPENAI_SECRET
    user_answers = attempt.answers

    bands = {}

    for answer in user_answers:
        section = attempt.module.sections.filter(id=int(answer)).first()
        task = section.task
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": writing_prompts.PROMPT0},
                {"role": "system", "content": f'TASK: {task}'},
                {"role": "user",
                    "content": f'User Answer: {user_answers[answer]}'},
                {"role": "system", "content": writing_prompts.PROMPT2},
                {"role": "system", "content": writing_prompts.PROMPT3},
                {"role": "system", "content": writing_prompts.PROMPT4},
            ]
        )
        content = sanitize_json_string(
            str(completion.choices[0].message["content"]))
        bands[section.id] = content

    attempt.evaluation_bands = bands
    attempt.save()
    return attempt


def openai_get_writing_evaluation(attempt):
    openai.api_key = settings.OPENAI_SECRET
    user_answers = attempt.answers

    evaluation = {}

    for answer in user_answers:
        section = attempt.module.sections.filter(id=int(answer)).first()
        task = section.task
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "user", "content": writing_prompts.PROMPT0},
                {"role": "user", "content": f'TASK: {task}'},
                {"role": "user",
                    "content": f'My Answer: {user_answers[answer]}'},
                {"role": "user", "content": writing_prompts.PROMPT71},
                {"role": "user", "content": writing_prompts.PROMPT8},
            ]
        )
        content = completion.choices[0].message["content"]
        evaluation[section.id] = content
    attempt.evaluation = evaluation
    attempt.save()
    return attempt


def sanitize_json_string(s):
    s = s.replace("'", '"')  # Replace single quotes with double quotes
    s = re.sub(r'\\(?![/uUnN"])', r'\\\\', s)  # Escape stray backslashes
    return s
