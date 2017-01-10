from category import urlpatterns as catpatterns
from django.conf.urls import include, url
from products import urlpatterns as prodpatterns
import product
from satchmo_utils.signals import collect_urls
from satchmo_store.shop import get_satchmo_setting

catbase = r'^' + get_satchmo_setting('CATEGORY_SLUG') + '/'
prodbase = r'^' + get_satchmo_setting('PRODUCT_SLUG') + '/'

urlpatterns = [
    url(prodbase, include('product.urls.products')),
    url(catbase, include('product.urls.category')),
]

collect_urls.send(product, section="__init__", patterns = urlpatterns)
