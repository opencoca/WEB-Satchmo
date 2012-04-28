from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from satchmo_store.shop.models import Order
from satchmo_utils.views import bad_or_missing
from payment.utils import gift_certificate_processor

def success(request):
    """
    The order has been succesfully processed.  This can be used to generate a receipt or some other confirmation
    """
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return bad_or_missing(request, _('Your order has already been processed.'))

    del request.session['orderID']
    # We check to see if there are any gift certificates in the order
    gc_email_sent = False
    gc_in_orderitems = len(filter(lambda x: 'GiftCertificateProduct' in x.product.get_subtypes(), order.orderitem_set.all()))
    if gc_in_orderitems:
        gc_email_sent = gift_certificate_processor(order)
    return render_to_response('shop/checkout/success.html',
                              {'order': order,
                              'gc_email_sent': gc_email_sent},
                              context_instance=RequestContext(request))
success = never_cache(success)

def failure(request):
    return render_to_response(
        'shop/checkout/failure.html',
        {},
        context_instance=RequestContext(request)
    )
