from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def overall_performance(request):
    student = request.user.student

    return Response({
        'average_score': student.average_score,
        'fifteen_days_chart': student.fifteen_days_chart,
    }, status=200)
