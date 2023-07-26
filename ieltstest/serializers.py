from rest_framework import serializers
from ieltstest.models import ListeningTest


class ListeningTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningTest
        fields = ['']
        