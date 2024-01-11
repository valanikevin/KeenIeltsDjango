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
    student = request.user.student

    attempts = student.attempts(
        modules=[module_type], module_limit=None, total_limit=None)

    return Response(attempts, status=200)
