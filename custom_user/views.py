
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from student.models import Student
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import json
import time
from custom_user.forms import UserCreationForm


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
def register_user(request):
    data = json.loads(request.body)
    form = UserCreationForm(data)
    if form.is_valid():
        user = form.save()

        Student.objects.create(user=user)

        data = {
            'type': 'success',
            'email': user.email,
            'message': 'Registration Successful.'
        }
        status = 200
    else:
        errors = eval(form.errors.as_json())

        data = {
            'type': 'error',
            'message': 'Registration Failed.',
            'errors': errors
        }
        status = 400
    return Response(status=status, data=data)
