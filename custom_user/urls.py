from django.urls import path
from . import views as user_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', user_views.register_user),
    path('token/', user_views.MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('update_account_settings/', user_views.update_account_settings,
         name='update_account_settings'),
    path('change_account_password/',
         user_views.change_account_password, name='change_password'),
    path('get_user_details/', user_views.get_user_details,),
]
