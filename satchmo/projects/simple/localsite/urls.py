from django.conf.urls import *


urlpatterns = patterns('',
    (r'example/', 'simple.localsite.views.example', {}),
)
