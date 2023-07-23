from django.urls import path
from leaderboard import views as leaderboard_views

urlpatterns = [
    path('', leaderboard_views.leaderboard),
]
