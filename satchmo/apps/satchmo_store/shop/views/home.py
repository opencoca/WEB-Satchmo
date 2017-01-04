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

    def get_queryset(self):
        return display_featured()

    def get_paginate_by(self, queryset):
        return config_value('PRODUCT','NUM_PAGINATED')
        
        
class HomeTemplateView(TemplateView):
    template_name = "shop/index.html"
    
    def get_context_data(self, **kwargs):
        if self.request.method == "GET":
            currpage = self.request.GET.get('page', 1)
        else:
            currpage = 1
        
        featured = display_featured()
        count = config_value('PRODUCT','NUM_PAGINATED')
        paginator = Paginator(featured, count)
        is_paged = False
        page = None
        try:
            paginator.validate_number(currpage)
        except InvalidPage:
            return bad_or_missing(self.request, _("Invalid page number"))
            
        is_paged = paginator.num_pages > 1
        page = paginator.page(currpage)

        context = super(HomeTemplateView, self).get_context_data(**kwargs)        
        context['all_products_list'] = page.object_list
        context['is_paginated'] = is_paged
        context['page_obj'] = page
        context['paginator'] = paginator
        
        return context    
