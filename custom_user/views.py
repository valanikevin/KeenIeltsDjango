
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
from custom_user.forms import AccountSettingForm, PasswordChangeForm

# Login Views


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['coachinginstitute_slug'] = user.student.institute.slug if user.student.institute else None

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
def register_user(request):
    data = json.loads(request.body)
    form = UserCreationForm(data)
    if form.is_valid():
        user = form.save(commit=False)
        user.generate_verification_code()
        user.save()

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_account_settings(request):
    form = AccountSettingForm(request.data, instance=request.user)

    if form.is_valid():
        form.save()
        user = request.user
        data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'testType': user.student.type,
            'coachinginstitute_slug': user.student.institute.slug if user.student.institute else None,
            'coachinginstitute_name': user.student.institute.name if user.student.institute else None,
            'message': 'Settings updated successfully',
        }
        return Response(data, status=200)
    else:
        return Response(form.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_account_password(request):
    form = PasswordChangeForm(request.user, request.data)

    if form.is_valid():
        form.save()
        return Response({'message': 'Password updated successfully'}, status=200)
    else:
        return Response(form.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    user = request.user
    data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'testType': user.student.type,
        'coachinginstitute_slug': user.student.institute.slug if user.student.institute else None,
        'coachinginstitute_name': user.student.institute.name if user.student.institute else None,
    }
    return Response(data=data)
