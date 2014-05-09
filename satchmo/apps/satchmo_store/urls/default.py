from django.conf import settings
from django.conf.urls import patterns, include
from django.conf.urls.static import static
from django.contrib import admin
import logging
import re

log = logging.getLogger('satchmo_store.urls')

# discover all admin modules - if you override this for your
# own base URLs, you'll need to autodiscover there.
admin.autodiscover()

urlpatterns = getattr(settings, 'URLS', [])

adminpatterns = patterns('',
     (r'^admin/', include(admin.site.urls)),
)

if urlpatterns:
    urlpatterns += adminpatterns
else:
    urlpatterns = adminpatterns
# If we are in debug mode, then serve the images and other files in MEDIA_ROOT
if settings.DEBUG and getattr(settings,'MEDIA_URL',False) and getattr(settings,'MEDIA_ROOT',False):
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

