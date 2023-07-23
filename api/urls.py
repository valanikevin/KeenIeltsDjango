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

    # Authentication
    path('register/', user_views.register_user),
    path('token/', user_views.MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
