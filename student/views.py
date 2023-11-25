from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def overall_performance(request):
    student = request.user.student

    return Response({
        'overall_feedback_date': student.overallperformancefeedback.updated_at.strftime("%B %d, %Y"),
        'overall_feedback': student.overall_feedback,
        'average_score': student.average_score,
        'fifteen_days_chart': student.fifteen_days_chart,
        'recent_tests': student.recent_tests,

    }, status=200)
