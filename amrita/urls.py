from django.urls import path
from amrita import views as amrita_views

urlpatterns = [
    path('', amrita_views.amrita),
]
