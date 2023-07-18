from django.urls import path
from api import views as api_views

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', api_views.getRoutes),
    path('token/', api_views.MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
