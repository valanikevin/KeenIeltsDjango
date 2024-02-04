import os
from django.shortcuts import render
from ieltstest.variables import get_individual_test_obj_serializer_from_slug, get_module_attempt_from_slug
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from ieltstest.serializers import BookModuleSerializer, FullTestAttemptSerializer, GetBookSerializer
from ieltstest.models import Book, Test, WritingAttempt, SpeakingSection, SpeakingAttempt, WritingSection, FullTestAttempt, FullTestAttempt, SpeakingSectionQuestion
from rest_framework.permissions import IsAuthenticated
import json
import io
import os
import re
import openai
from django.conf import settings
from ieltstest.openai import writing_prompts
from django.core import serializers
from moviepy.editor import AudioFileClip
from io import BytesIO
import tempfile
from moviepy.editor import AudioFileClip
from django.core.files.base import ContentFile
import subprocess


def ieltstest(request):
    pass


@api_view(['GET'])
def get_book(request, book_slug):
    book = Book.objects.get(slug=book_slug)
    student_test_type = request.user.student.type if request.user.is_authenticated else 'academic'
    test_type = request.GET.get('testType', student_test_type)

    serializer = GetBookSerializer(
        book, context={'test_type': test_type}, many=False)

    return Response(serializer.data)


def get_books():
    books = Book.objects.filter(status="published").order_by('priority')
    return books


@api_view(['GET'])
def module_home(request, slug):
    books = get_books()
    student_test_type = request.user.student.type if request.user.is_authenticated else 'academic'
    test_type = request.GET.get('testType', student_test_type)

    if test_type and request.user.is_authenticated and request.user.student.type is not test_type:
        student = request.user.student
        student.type = test_type
        student.save()

    serializer = BookModuleSerializer(
        books, context={'module_slug': slug, 'test_type': test_type}, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_smart_test_from_book(request, module_type, book_slug):
    IndividualModule, IndividualModuleSerializer = get_individual_test_obj_serializer_from_slug(
        module_type)

    IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
        module_type)

    modules = IndividualModule.objects.filter(
        test__book__slug=book_slug, status="published")

    # Get the slugs of modules that the user has already attempted
    attempted_module_slugs = IndividualModuleAttempt.objects.filter(
        user=request.user,
        module__test__book__slug=book_slug
    ).values_list('module__slug', flat=True).distinct()

    specific_test = request.POST.get('specific_test')

    if specific_test:
        selected_module = modules.filter(test__slug=specific_test)
    else:
        # Exclude the modules that the user has already attempted
        selected_module = modules.exclude(
            slug__in=attempted_module_slugs).order_by('?')
        if not selected_module.exists():
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
def find_smart_test_from_module(request, module_type):
    IndividualModule, IndividualModuleSerializer = get_individual_test_obj_serializer_from_slug(
        module_type)
    IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
        module_type)
    modules = IndividualModule.objects.filter(status="published").order_by('?')

    if modules.exists():
        selected_module = modules.first()
        attempt = IndividualModuleAttempt.objects.create(
            user=request.user, module=selected_module)
    else:
        return Response(status=500)
    return Response({'module_type': module_type, 'selected_module': selected_module.slug, 'attempt': attempt.slug})


@api_view(['POST'])
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
    IndividualModule, IndividualModuleSerializer = get_individual_test_obj_serializer_from_slug(
        module_type)
    IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
        module_type)

    attempt = IndividualModuleAttempt.objects.get(slug=attempt_slug)

    timestamps = parse_post_data(request)

    save_audio_files(request, attempt)

    attempt.merge_audio_timestamps(timestamps)

    attempt.status = 'Completed'
    attempt.internal_status = 'Completed'

    attempt.save()

    data = {'status': attempt.status}
    return Response(data=data)


def parse_post_data(request):
    timestamps = {}
    _timestamps = {}
    for key, value in request.POST.items():
        if key != 'attempt_type' and key != 'fullAudio':
            main_key, nested_key = key.split(',')
            timestamps.setdefault(int(main_key), {})[
                int(nested_key)] = json.loads(value)

    for item in timestamps:
        for time in timestamps[item]:
            _timestamps[time] = timestamps[item][time]['elapsedTime']

    return _timestamps


def convert_wav_to_mp3(blob):
    # Create a temporary file for the input WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
        # Write the blob to the temporary file
        for chunk in blob.chunks():
            temp_wav.write(chunk)
        temp_wav.flush()  # Ensure all data is written to the file
        input_path = temp_wav.name

    # Define the output path for the MP3 file (also temporary)
    output_path = tempfile.mktemp(suffix='.mp3')

    # Use ffmpeg to convert WAV to MP3
    subprocess.run(['ffmpeg', '-i', input_path, '-vn', '-ar', '44100',
                   '-ac', '2', '-b:a', '192k', output_path], check=True)

    # Read the converted MP3 file
    with open(output_path, 'rb') as mp3_file:
        mp3_content = mp3_file.read()

    # Clean up temporary files
    os.remove(input_path)
    os.remove(output_path)

    # Return the MP3 content in a format that can be saved
    return ContentFile(mp3_content)


def save_audio_files(request, attempt):
    for section_id, audio_blob in request.FILES.items():
        if section_id == "fullAudio":
            mp3_audio = convert_wav_to_mp3(audio_blob)
            attempt.merged_audio.save(
                f'{attempt.slug}.mp3', ContentFile(mp3_audio.read()))

    return True


def update_attempt_status(request, attempt):
    attempt_type = request.POST.get('attempt_type')
    attempt.status = attempt_type
    attempt.save()


@api_view(['POST'])
def get_attempt(request, module_type, attempt_slug):
    IndividualModuleAttempt, IndividualModuleAttemptSerializer = get_module_attempt_from_slug(
        module_type)
    attempt = IndividualModuleAttempt.objects.get(slug=attempt_slug)
    print(f'Status: {attempt.status}')
    if attempt.status == "Ready":
        attempt.internal_status = "Evaluated"
        attempt.status = "Evaluated"
        attempt.save()
    serializer = IndividualModuleAttemptSerializer(attempt,  many=False)
    return Response(serializer.data)


@api_view(['POST'])
def get_writing_evaluation(request, attempt_slug, section_id):
    attempt = WritingAttempt.objects.get(slug=attempt_slug)
    section = WritingSection.objects.get(id=section_id)
    evaluation = attempt.get_evaluation(section=section)
    return Response(evaluation)


@api_view(['POST'])
def get_speaking_evaluation(request, attempt_slug):
    attempt = SpeakingAttempt.objects.get(slug=attempt_slug)

    return Response(attempt.get_evaluation())


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_smart_test_from_book_fulltest(request, book_slug):
    book = Book.objects.get(slug=book_slug)

    # Get the IDs of tests that the user has already attempted
    attempted_test_ids = FullTestAttempt.objects.filter(
        user=request.user,
        test__book__slug=book_slug
    ).values_list('test__id', flat=True).distinct()

    specific_test = request.POST.get('specific_test')

    if specific_test:
        test = Test.objects.filter(slug=specific_test).exclude(
            id__in=attempted_test_ids).first()
        if not test:
            return Response(status=500)  # Or handle it differently
    else:
        # Exclude the tests that the user has already attempted
        test = Test.objects.filter(book__slug=book_slug).exclude(
            id__in=attempted_test_ids).order_by('?').first()
        if not test:
            test = Test.objects.filter(
                book__slug=book_slug).order_by('?').first()

    fulltest_attempt = FullTestAttempt.objects.create(
        user=request.user, test=test)

    fulltest_attempt.create_empty_attempts(
        book_slug=book_slug, user=request.user, specific_test=specific_test)
    return Response({'book_slug': book_slug, 'attempt': fulltest_attempt.slug})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_fulltest_info(request, attempt_slug):
    attempt = FullTestAttempt.objects.get(slug=attempt_slug)
    serializer = FullTestAttemptSerializer(attempt, many=False)
    return Response(serializer.data)
