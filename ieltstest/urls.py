from django.urls import path
from ieltstest import views as tests_views

urlpatterns = [
    path('', tests_views.ieltstest, name='ieltstest_home'),
    path('<slug:slug>/', tests_views.module_home, name='module_home'),
    path('find_smart_test/<slug:module_type>/<slug:book_slug>/',
         tests_views.find_smart_test_from_book, name='find_smart_test_from_book'),

    # Attempts
    path('get_module/<slug:module_type>/<slug:module_slug>/',
         tests_views.get_module, name='get_module'),
    path('update_attempt/<slug:module_type>/<slug:attempt_slug>/',
         tests_views.update_attempt, name='update_attempt'),
    path('get_attempt/<slug:module_type>/<slug:attempt_slug>/',
         tests_views.get_attempt, name='get_attempt'),
]
