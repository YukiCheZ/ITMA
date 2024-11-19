from django.urls import path
from . import views

urlpatterns = [
    path('set_api_key/', views.set_api_key, name='set_api_key'), 
]