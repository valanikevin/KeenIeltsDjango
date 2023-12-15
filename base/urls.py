from django.urls import path, include
from base import views as base_views
from custom_user import views as user_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('report_mistake/', base_views.report_mistake, name='report_mistake'),
    path('add_comment/', base_views.add_comment, name='add_comment'),
    path('get_comments/<slug:unique_id>/', base_views.get_comments, name='get_comments'),
]
