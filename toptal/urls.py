from django.conf.urls import patterns, include, url
from toptal.views import *
from django.views.generic import TemplateView
import os.path

from todo.api import TodoResource, UserResource
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(TodoResource())

urlpatterns = patterns('',

    url(r'^$', home_page),
    url(r'^login/$', login_user, name='todo_login'),
    url(r'^logout/$', logout_user),
    url(r'^register/$', register_user),
    url(r'^settings/$', change_settings),
    url(r'^settings/api/$', TemplateView.as_view(template_name="api.html")),
    url(r'^password/change/$', 'django.contrib.auth.views.password_change'),    
    url(r'^password/change/done$', 'django.contrib.auth.views.password_change_done'),    

    # ToDo list app
    url(r'^todo/', include('todo.urls')),
    
    # API
    url(r'^api/', include(v1_api.urls)),
)
