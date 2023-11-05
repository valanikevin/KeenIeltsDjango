from django.urls import path
from ieltstest import views as tests_views

urlpatterns = [
    path('', tests_views.ieltstest, name='ieltstest_home'),
    path('<slug:slug>/', tests_views.module_home, name='module_home'),
    path('find_smart_test/fulltest/<slug:book_slug>/',
         tests_views.find_smart_test_from_book_fulltest, name='find_smart_test_from_book_fulltest'),
    path('find_smart_test/<slug:module_type>/<slug:book_slug>/',
         tests_views.find_smart_test_from_book, name='find_smart_test_from_book'),

    # Attempts
    path('get_module/<slug:module_type>/<slug:module_slug>/',
         tests_views.get_module, name='get_module'),
    path('update_attempt/speaking/<slug:attempt_slug>/',
         tests_views.update_attempt_speaking, name='update_attempt_speaking'),
    path('update_attempt/<slug:module_type>/<slug:attempt_slug>/',
         tests_views.update_attempt, name='update_attempt'),
    path('get_attempt/<slug:module_type>/<slug:attempt_slug>/',
         tests_views.get_attempt, name='get_attempt'),

    # Writing
    path('get_writing_evaluation/<slug:attempt_slug>/<int:section_id>/',
         tests_views.get_writing_evaluation, name='get_writing_evaluation'),

    # Speaking
    path('get_speaking_evaluation/<slug:attempt_slug>/',
         tests_views.get_speaking_evaluation, name="get_speaking_evaluation"),

]
