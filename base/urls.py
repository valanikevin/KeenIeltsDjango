from django.urls import path, include
from base import views as base_views
from custom_user import views as user_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('report_mistake/', base_views.report_mistake, name='report_mistake'),
]
