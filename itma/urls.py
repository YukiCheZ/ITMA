from django.urls import path
from django.contrib import admin
from django.shortcuts import redirect

from system import views as system_views

from llmagent import views as llmagent_views

from taskcalendar import views as taskcalendar_views

urlpatterns = [
    path('', lambda request: redirect('login')),
    path('admin/', admin.site.urls),
    path('home/', system_views.home, name='home'),
    path('login/', system_views.login_view, name='login'),
    path('logout/', system_views.logout_view, name='logout'),
    path('register/', system_views.register_view, name='register'),
    
    path('taskcalendar/', taskcalendar_views.taskcalendar, name='taskcalendar'),
    path('all_events/', taskcalendar_views.all_events, name='all_events'),
    path('show_all_events/', taskcalendar_views.show_all_events, name='show_all_events'),
    path('add_event/', taskcalendar_views.add_event, name='add_event'),
    path('update/', taskcalendar_views.update, name='update'),
    path('remove/', taskcalendar_views.remove, name='remove'),
    path('mark_completed/', taskcalendar_views.mark_completed, name='mark_completed'),

    path('llmagent/', llmagent_views.chatglm_view, name='llmagent'),
    path('set_api_key/', llmagent_views.set_api_key, name='set_api_key'), 
]
