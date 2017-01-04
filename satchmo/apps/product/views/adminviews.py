from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.db import IntegrityError
from product.forms import VariationManagerForm, InventoryForm, ProductExportForm, ProductImportForm
from product.models import Product
from product.modules.configurable.models import ConfigurableProduct
from satchmo_utils.views import bad_or_missing
import logging

log = logging.getLogger('product.views.adminviews')

def edit_inventory(request):
    """A quick inventory price, qty update form"""
    if request.method == "POST":
        new_data = request.POST.copy()
        form = InventoryForm(new_data)
        if form.is_valid():
            form.save(request)
            url = urlresolvers.reverse('satchmo_admin_edit_inventory')
            return HttpResponseRedirect(url)
    else:
        form = InventoryForm()

    ctx = {
        'title' : _('Inventory Editor'),
        'form' : form
    }

    return render(request, 'product/admin/inventory_form.html', ctx)

edit_inventory = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(edit_inventory)

def export_products(request, template='product/admin/product_export_form.html'):
    """A product export tool"""
    if request.method == 'POST':
        new_data = request.POST.copy()
        form = ProductExportForm(new_data)
        if form.is_valid():
            return form.export(request)
    else:
        form = ProductExportForm()
    fileform = ProductImportForm()


    ctx = {
        'title' : _('Product Import/Export'),
        'form' : form,
        'importform': fileform
    }

    return render(request, template, ctx)

export_products = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(export_products)

def import_products(request, maxsize=10000000):
    """
    Imports product from an uploaded file.
    """

    if request.method == 'POST':
        errors = []
        results = []
        if 'upload' in request.FILES:
            infile = request.FILES['upload']
            form = ProductImportForm()
            results, errors = form.import_from(infile, maxsize=maxsize)

        else:
            errors.append('File: %s' % request.FILES.keys())
            errors.append(_('No upload file found'))

        ctx = {
            'errors' : errors,
            'results' : results
        }
        return render(request, "product/admin/product_import_result.html", ctx)
    else:
        url = urlresolvers.reverse('satchmo_admin_product_export')
        return HttpResponseRedirect(url)

import_products = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(import_products)

# def product_active_report(request):
#
#     products = Product.objects.filter(active=True)
#     products = [p for p in products.all() if 'productvariation' not in p.get_subtypes]
#     ctx = {title: 'Active Product Report', 'products' : products }
#     return render(request, 'product/admin/active_product_report.html', ctx)
#
# product_active_report = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(product_active_report)

def variation_list(request):
    products = Product.objects.filter(configurableproduct__in = ConfigurableProduct.objects.all())
    return render(request, 'product/admin/variation_manager_list.html', { 'products' : products })


def variation_manager(request, product_id = ""):
    try:
        product = Product.objects.get(id=product_id)
        subtypes = product.get_subtypes()

        if 'ProductVariation' in subtypes:
            # got a variation, we want to work with its parent
            product = product.productvariation.parent.product
            if 'ConfigurableProduct' in product.get_subtypes():
                url = urlresolvers.reverse("satchmo_admin_variation_manager",
                    kwargs = {'product_id' : product.id})
                return HttpResponseRedirect(url)

        if 'ConfigurableProduct' not in subtypes:
            return bad_or_missing(request, _('The product you have requested is not a Configurable Product.'))

    except Product.DoesNotExist:
            return bad_or_missing(request, _('The product you have requested does not exist.'))

    if request.method == 'POST':
        new_data = request.POST.copy()
        form = VariationManagerForm(new_data, product=product)
        if form.is_valid():
            log.debug("Saving form")
            try:
                form.save(request)
            except IntegrityError:
                messages.error(request, _('The product you are attempting to remove is linked to an order and can not be removed.'))
            # rebuild the form
            form = VariationManagerForm(product=product)
        else:
            log.debug('errors on form')
    else:
        form = VariationManagerForm(product=product)

    ctx = {
        'product' : product,
        'form' : form,
    }
    return render(request, 'product/admin/variation_manager.html', ctx)

variation_manager = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')(variation_manager)
