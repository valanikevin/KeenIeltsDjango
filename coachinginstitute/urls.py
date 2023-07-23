from django.urls import path
from coachinginstitute import views as institute_views

urlpatterns = [
    path('', institute_views.coachinginstitute),
]
