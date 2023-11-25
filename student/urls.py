from django.urls import path
from student import views as student_views

urlpatterns = [
    path('overall_performance/',
         student_views.overall_performance, name='overall_performance'),
]
