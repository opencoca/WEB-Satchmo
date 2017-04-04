from django.views.generic import ListView

from livesettings.functions import config_value
from satchmo_ext.productratings.queries import highest_rated


class BestratingsListView(ListView):
    #model = Product
    template_name = "product/best_ratings.html"
    context_object_name = "products"
    count = 0

    def get_queryset(self):
        count = config_value('PRODUCT','NUM_DISPLAY') if self.count is None else self.count
        return highest_rated(count)

display_bestratings = BestratingsListView.as_view()
        
# def display_bestratings(request, count=0, template='product/best_ratings.html'):
#     """Display a list of the products with the best ratings in comments"""
#     if count is None:
#         count = config_value('PRODUCT','NUM_DISPLAY')

#     return render(request, template, {
#         'products' : highest_rated(),
#     })