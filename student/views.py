from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ieltstest.variables import get_module_attempt_from_slug
from ieltstest.serializers import ListeningAttemptSerializer, ReadingAttemptSerializer, WritingAttemptSerializer, SpeakingAttemptSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def overall_performance(request):
    student = request.user.student
    total_tests = student.average_score["overall"]["total_attempts"]
    if total_tests == 0:
        return Response({
            'average_score': student.average_score,
            'fifteen_days_chart': None,
            'recent_tests': None,
        }, status=200)
    try:
        data = {
            'average_score': student.average_score,
            'fifteen_days_chart': student.fifteen_days_chart,
            'recent_tests': student.attempts(),

        }
    except Exception as e:
        data = {
            'exception': str(e)
        }
    return Response(data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def overall_performance_feedback(request):
    student = request.user.student
    total_tests = student.average_score["overall"]["total_attempts"]
    if total_tests == 0:
        return Response({
            'overall_feedback_date': None,
            'overall_feedback': None,
        }, status=200)
    try:
        data = {
            'overall_feedback_date': student.overallperformancefeedback.updated_at.strftime("%B %d, %Y") if student.overallperformancefeedback else None,
            'overall_feedback': student.overall_feedback,


        }
    except Exception as e:
        data = {
            'exception': str(e)
        }
    return Response(data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_attempts_from_book(request, book_slug):
    student = request.user.student
    attempts = student.attempts(book_slug=book_slug)

    return Response(attempts, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_attempts(request, module_type):
    Attempt, AttemptSerializer = get_module_attempt_from_slug(module_type)

    attempts = Attempt.objects.filter(
        user=request.user).order_by('-created_at')

    attempts_list = []

    for attempt in attempts:

        attempts_list.append(
            {
                'slug': attempt.slug,
                'module_type': module_type,
                'module_slug': attempt.module.slug,
                'book_name': attempt.module.test.book.name,
                'module_name': attempt.module.name,
                'status': attempt.status,
                'updated_at': attempt.updated_at.strftime("%B %d, %Y"),
                'bands': attempt.bands,

            }
        )

    return Response(attempts_list, status=200)
