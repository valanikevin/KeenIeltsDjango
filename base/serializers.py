from base.models import CommentMain, CommentItem
from rest_framework import serializers
from django.utils.timesince import timesince
from datetime import datetime, timedelta


class CommentItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    short_date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CommentItem
        fields = ['name', 'comment', 'short_date']

    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_short_date(self, obj):
        now = datetime.now(obj.created_at.tzinfo)
        if now - obj.created_at < timedelta(minutes=1):
            return "just now"
        elif now - obj.created_at < timedelta(days=7):
            # Return the timesince for up to 7 days
            return timesince(obj.created_at).split(",")[0] + " ago"
        else:
            # Return the formatted date for older comments
            return obj.created_at.strftime("%b %d, %Y")


class CommentMainSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CommentMain
        fields = '__all__'

    def get_comments(self, obj):
        comments = obj.comments()
        serializer = CommentItemSerializer(comments, many=True)
        return serializer.data
