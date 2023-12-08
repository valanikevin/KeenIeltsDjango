from django.urls import path
from student import views as student_views

urlpatterns = [
    path('overall_performance/',
         student_views.overall_performance, name='overall_performance'),
    path('get_attempts_from_book/<slug:book_slug>/', student_views.get_attempts_from_book,
         name='get_attempts_from_book'),
]
