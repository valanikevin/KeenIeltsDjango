from django.urls import path
from student import views as student_views

urlpatterns = [
    path('', student_views.student),
]
