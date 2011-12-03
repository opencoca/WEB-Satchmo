"""
Satchmo shipping module using python-fedex

"""

# Note, make sure you use decimal math everywhere!
from decimal import Decimal
from django.utils.translation import ugettext as _
from shipping.modules.base import BaseShipper
from livesettings import config_get_group
from fedex.services.rate_service import FedexRateServiceRequest

import logging

log = logging.getLogger('fedex_web_services.shipper')

transit_days = {
    'FEDEX_1_DAY_FREIGHT': '1 day',
    'FEDEX_2_DAY': '2 days',
    'FEDEX_2_DAY_FREIGHT': '2 days',
    'FEDEX_3_DAY_FREIGHT': '3 days',
    'FEDEX_EXPRESS_SAVER': '3 days',
    'FEDEX_GROUND': '1 to 7 days',
    'FIRST_OVERNIGHT': '1 day',
    'GROUND_HOME_DELIVERY': '1 to 7 days',
    'PRIORITY_OVERNIGHT': '1 day',
    'SMART_POST': '2 to 8 days',
    'STANDARD_OVERNIGHT': '1 day',
}

class Shipper(BaseShipper):

    id = "fedex_web_services"
    
    def __init__(self, cart=None, contact=None, service_type=None, config=None, packaging=None, default_weight=None):
        
        self._calculated = False
        self.cart = cart
        self.contact = contact
        
        if service_type:    
            self.service_type_code = service_type[0]
            self.service_type_text = service_type[1]

        else:
            self.service_type_code = '99'
            self.service_type_text = 'Uninitialized'

        self.id = u'%s' % (self.service_type_text)
        
        self._cost = Decimal('0.00')
        self._valid = None
        self.CONFIG_OBJ = config
        self.packaging = packaging
        self.default_weight = default_weight
        try:
            self._expected_delivery = transit_days[self.service_type_code]
        except KeyError:
            self._expected_delivery = ''
        
    def __unicode__(self):
        return u"Shipping via fedex_web_services"
        
    def description(self):
        return _('Fedex - %s' % self.service_type_text)

    def cost(self):
        if self._calculated:
            return self._cost

    def method(self):
        return self.service_type_text

    def expectedDelivery(self):
        return self._expected_delivery

    def valid(self, order=None):
        if self._calculated:
            return self._valid
    
    def calculate(self, cart, contact):
        # These imports are here to avoid circular import errors
        from satchmo_store.shop.models import Config
        from shipping.utils import product_or_parent
        shop_details = Config.objects.get_current()
        
        settings = config_get_group('shipping.modules.fedex_web_services')
        
        verbose = settings.VERBOSE_LOG.value
        
        if verbose:
            log.debug('Calculating fedex with type=%s', self.service_type_code)
        
        rate_request = FedexRateServiceRequest(self.CONFIG_OBJ)
        # This is very generalized, top-level information.
        # REGULAR_PICKUP, REQUEST_COURIER, DROP_BOX, BUSINESS_SERVICE_CENTER or STATION
        rate_request.RequestedShipment.DropoffType = settings.DROPOFF_TYPE.value

        # See page 355 in WS_ShipService.pdf for a full list. Here are the common ones:
        # STANDARD_OVERNIGHT, PRIORITY_OVERNIGHT, FEDEX_GROUND, FEDEX_EXPRESS_SAVER
        rate_request.RequestedShipment.ServiceType = self.service_type_code
        
        # What kind of package this will be shipped in.
        # FEDEX_BOX, FEDEX_PAK, FEDEX_TUBE, YOUR_PACKAGING
        rate_request.RequestedShipment.PackagingType = self.packaging

        # No idea what this is.
        # INDIVIDUAL_PACKAGES, PACKAGE_GROUPS, PACKAGE_SUMMARY 
        rate_request.RequestedShipment.PackageDetail = 'INDIVIDUAL_PACKAGES'

        # Shipper's address
        rate_request.RequestedShipment.Shipper.Address.PostalCode = shop_details.postal_code
        rate_request.RequestedShipment.Shipper.Address.CountryCode = shop_details.country.iso2_code
        rate_request.RequestedShipment.Shipper.Address.Residential = False

        # Recipient address
        rate_request.RequestedShipment.Recipient.Address.PostalCode = contact.shipping_address.postal_code
        rate_request.RequestedShipment.Recipient.Address.CountryCode = contact.shipping_address.country.iso2_code
        # This flag is optional. When turned on, it limits flexibility in options you can select
        #rate_request.RequestedShipment.Recipient.Address.Residential = True

        # Who pays for the rate_request?
        # RECIPIENT, SENDER or THIRD_PARTY
        rate_request.RequestedShipment.ShippingChargesPayment.PaymentType = 'SENDER' 
        
        #EDT is used to determine which estimated taxes and duties are included in the response
        #For international shipments only
        rate_request.RequestedShipment.EdtRequestType = 'NONE'

        seq = 1
        # If we are using one, box we add up all the weights and ship in one box
        # Otherwise, we send multiple boxes
        box_weight = 0.0
        if settings.SINGLE_BOX.value:
            for product in cart.get_shipment_list():
                item_weight = product_or_parent(product, 'weight')
                if item_weight is None or item_weight < self.default_weight:
                    item_weight = float(self.default_weight)
                box_weight += item_weight
            # Valid weight units are only KG or LB
            if product.smart_attr('weight_units') and product.smart_attr('weight_units') != "":
                box_weight_units = product.smart_attr('weight_units')
            else:
                box_weight_units = settings.DEFAULT_WEIGHT_UNITS.value
            item = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
            item.SequenceNumber = seq
            item.Weight = rate_request.create_wsdl_object_of_type('Weight')
            item.Weight.Units = box_weight_units
            item.Weight.Value = box_weight
            item.PhysicalPackaging = 'BOX'
            rate_request.add_package(item)
        else: # Send separate packages for each item
            for product in cart.get_shipment_list():
                item_weight = product_or_parent(product, 'weight')
                if item_weight is None or item_weight < self.default_weight:
                    item_weight = float(self.default_weight)
                # Valid weight units are only KG or LB
                if product.smart_attr('weight_units') and product.smart_attr('weight_units') != "":
                    item_weight_units = product.smart_attr('weight_units')
                else:
                    item_weight_units = settings.DEFAULT_WEIGHT_UNITS.value
                item = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
                item.SequenceNumber = seq
                item.Weight.Units = item_weight_units
                item.Weight.Value = item_weight
                item.PhysicalPackaging = 'BOX'
                rate_request.add_package(item)
                seq += 1

        # If you'd like to see some documentation on the ship service WSDL, un-comment
        # this line. (Spammy).
        #print rate_request.client

        # Un-comment this to see your complete, ready-to-send request as it stands
        # before it is actually sent. This is useful for seeing what values you can
        # change.
        # print rate_request.RequestedShipment
        # Fires off the request, sets the 'response' attribute on the object.
        try:
            rate_request.send_request()
        except:
            pass
        # This will show the reply to your rate_request being sent. You can access the
        # attributes through the response attribute on the request object. This is
        # good to un-comment to see the variables returned by the FedEx reply.
        # print rate_request.response

        if rate_request.response.HighestSeverity in ['SUCCESS', 'WARNING', 'NOTE']:
            # we're good
            log.debug('******************good shipping: %s' % self.service_type_code)
            try:
                self._expected_delivery = rate_request.response.RateReplyDetails[0].TransitTime
            except AttributeError: # TransitTime not included for everything
                pass
            cost = 0
            for rate_detail in rate_request.response.RateReplyDetails[0].RatedShipmentDetails:
                cost = max(cost, rate_detail.ShipmentRateDetail.TotalNetFedExCharge.Amount)
            self._cost = Decimal(str(cost))
            self._valid = True
        else:
            log.debug('*******************bad shipping: %s' % self.service_type_code)
            log.debug(rate_request.response.HighestSeverity)
            log.debug(rate_request.response.Notifications)
            self._valid = False
        self._calculated = True
