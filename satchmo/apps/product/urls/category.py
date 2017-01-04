from django.conf.urls import url

from product.views import category_view, category_index

urlpatterns = [
    url(r'^(?P<parent_slugs>([-\w]+/)*)?(?P<slug>[-\w]+)/$', category_view, name='satchmo_category'),
    url(r'^$', category_index, name='satchmo_category_index'),
]