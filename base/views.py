from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from base.models import Issue


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_mistake(request):
    type = request.data['issueType']
    description = request.data['issueDescription']
    url = request.data['currentUrl']

    issue = Issue.objects.create(
        type=type,
        description=description,
        user=request.user,
        url=url
    )

    return Response({}, status=200)
