from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from . import views
from taskcalendar import views as taskcalendar_views
from llmagent import views as llmagent_views
from django.contrib.auth import views as auth_views
from django.urls import path


urlpatterns = [
    path('', lambda request: redirect('login')),
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    
    path('taskcalendar/', taskcalendar_views.taskcalendar, name='taskcalendar'),
    path('all_events/', taskcalendar_views.all_events, name='all_events'),
    path('show_all_events/', taskcalendar_views.show_all_events, name='show_all_events'),
    path('add_event/', taskcalendar_views.add_event, name='add_event'),
    path('update/', taskcalendar_views.update, name='update'),
    path('remove/', taskcalendar_views.remove, name='remove'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    path('llmagent/', llmagent_views.chatglm_view, name='llmagent'),
    path('set_api_key/', llmagent_views.set_api_key, name='set_api_key'), 
]