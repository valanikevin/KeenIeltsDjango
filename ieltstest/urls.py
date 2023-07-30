from django.urls import path
from ieltstest import views as tests_views

urlpatterns = [
    path('', tests_views.ieltstest, name='ieltstest_home'),
    path('<slug:slug>/', tests_views.module_home, name='module_home'),
    path('<slug:test_type>/find_smart_test/<slug:book_slug>/',
         tests_views.find_smart_test_from_book, name='find_smart_test_from_book'),

]
