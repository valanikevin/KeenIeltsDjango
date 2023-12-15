from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from base.models import Issue, CommentMain, CommentItem
from base.serializers import CommentMainSerializer


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request):
    unique_id = request.data['unique_id']
    comment = request.data['comment']
    user = request.user

    comment_main = CommentMain.objects.get_or_create(unique_id=unique_id)[0]
    comment_item = CommentItem.objects.create(
        main=comment_main,
        user=user,
        comment=comment
    )

    return Response({}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_comments(request, unique_id):
    comment_main = CommentMain.objects.filter(unique_id=unique_id)
    if comment_main.exists():
        comment_main = comment_main.first()
        serializer = CommentMainSerializer(comment_main, many=False)
    else:
        serializer = CommentMainSerializer(None, many=False)
    return Response(serializer.data, status=200)
