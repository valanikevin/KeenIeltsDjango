from django.urls import path, include
from api import views as api_views
from custom_user import views as user_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', api_views.getRoutes),

    # App Views
    path('amrita/', include('amrita.urls')),
    path('coachinginstitute/', include('coachinginstitute.urls')),
    path('ieltstest/', include('ieltstest.urls')),
    path('leaderboard/', include('leaderboard.urls')),
    path('student/', include('student.urls')),
    path('account/', include('custom_user.urls')),
]
