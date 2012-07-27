from django.conf.urls.defaults import *
from todo.views import *


urlpatterns = patterns('',

    # User's home page (when logged in)
    url(r'^$', index),
    url(r'^(?P<pk>\d+)/delete/', delete),
    url(r'^(?P<pk>\d+)/edit/', edit),
    url(r'^add/', add),  

)

