from django.views.generic import TemplateView, ListView
from django.core.paginator import Paginator, InvalidPage
from django.utils.translation import ugettext as _

from livesettings.functions import config_value

from product.models import Product
from product.views import display_featured
from satchmo_utils.views import bad_or_missing


class HomeListView(ListView):
    model = Product
    template_name = "shop/index.html"
    context_object_name = "all_products_list"

    def get_queryset(self):
        return display_featured()

    def get_paginate_by(self, queryset):
        return config_value('PRODUCT','NUM_PAGINATED')