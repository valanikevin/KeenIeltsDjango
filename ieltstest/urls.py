from django.urls import path
from ieltstest import views as tests_views

urlpatterns = [
    path('', tests_views.ieltstest, name='ieltstest_home'),
]
