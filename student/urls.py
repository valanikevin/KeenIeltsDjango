from django.urls import path
from student import views as student_views

urlpatterns = [
    path('overall_performance/',
         student_views.overall_performance, name='overall_performance'),
    path('overall_performance_feedback/',
         student_views.overall_performance_feedback, name='overall_performance_feedback'),
    path('get_attempts_from_book/<slug:book_slug>/', student_views.get_attempts_from_book,
         name='get_attempts_from_book'),
    path('get_attempts/<slug:module_type>/',
         name="get_attempts", view=student_views.get_attempts),
]
