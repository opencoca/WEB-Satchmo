from django.conf.urls import *

from satchmo_store.urls import urlpatterns

urlpatterns += patterns('',
    (r'test/', include('simple.localsite.urls'))
)
