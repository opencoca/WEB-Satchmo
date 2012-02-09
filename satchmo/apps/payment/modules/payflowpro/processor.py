import random

from datetime import datetime
from decimal import Decimal
from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _
from payment.modules.base import BasePaymentProcessor, ProcessorResult
from satchmo_store.shop.models import Config
from satchmo_utils.numbers import trunc_decimal
from tax.utils import get_tax_processor

from payflowpro.client import PayflowProClient

class PaymentProcessor(BasePaymentProcessor):
    """
    PayflowPro payment processing module
    You must have an account with PayPal in order to use this module.
    """
    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('payflowpro', settings)
        partner = self.settings.PARTNER.value
        vendor = self.settings.VENDOR.value
        username = self.settings.USER.value
        password = self.settings.PASSWORD.value
        testing = not self.settings.LIVE.value
        if testing:
            url_base = PayflowProClient.URL_BASE_TEST
        else:
            url_base = PayflowProClient.URL_BASE_LIVE

        self.payflow = PayflowProClient(partner=partner, vendor=vendor,
                                        username=username, password=password,
                                        url_base=url_base)

    def get_charge_data(self, amount=None):
        """
        Build the dictionary needed to process a credit card charge.

        Return: a dictionary with the following key-values:
            * log_string: the transaction data without the sensible
                           buyer data. Suitable for logs.
            * credit_card, amount, address, ship_address, customer_info :
                 the payflowpro.classes.* instances to be passed to
                 self.payflowpro
        """
        order = self.order
        if amount is None:
            amount = order.balance
        balance = trunc_decimal(amount, 2)

        ret = {
            'credit_card': CreditCard(
                acct=order.credit_card.decryptedCC,
                expdate="%d%d" % (order.credit_card.expire_year,
                                  order.credit_card.expire_month),
                cvv2=order.credit_card.cvv,
                ),
            
            'amount': Amount(amt=balance,),

            'address': Address(
                street=order.full_bill_street,
                zip=order.bill_postal_code,
                city=order.bill_city,
                state=order.bill_state,
                country=order.bill_country,
                ),

            'ship_address': ShippingAddress(
                shiptostreet=order.full_ship_street,
                shiptocity=order.ship_city,
                shiptofirstname=order.ship_first_name,
                shiptolastname=order.ship_last_name,
                shiptostate=order.ship_state,
                shiptocountry=order.ship_country,
                shiptozip=order.ship_postal_code,
                ),

            'customer_info': CustomerInfo(
                firstname=order.contact.first_name,
                lastname=order.contact.last_name,
                ),
            }

        redacted_data = ret.copy()
        redacted_data['credit_card'] = {
            'acct': order.credit_card.display_cc,
            'expdate': "%d%d" % (order.credit_card.expire_year,
                                 order.credit_card.expire_month),
            'cvv2': "REDACTED",
            }

        dicts = [getattr(d, 'data', d) for d in redacted_data.values()]
        ret['log_string'] = "\n".join("%s: %s" % (k, v) for d in dicts
                                      for k, v in d.items())

        return ret

    def _handle_unconsumed(self, unconsumed_data):
        """
        Handler for when we've got unconsumed data from the response
        """
        if unconsumed_data:
            self.log.warn("Something went wrong with python-payflowpro. "
                          "We got some unconsumed data: %s" % 
                          str(unconsumed_data))

    def _log_responses(self, responses):
        """
        Log the responses from PayflowPro for debugging
        """
        self.log_extra("Response variables from payflowpro:")
        for response in responses:
            self.log_extra("%(classname)s: %(response_fields)s" % {
                    'classname': response.__class__.__name__,
                    'response_fields': "%s" % response.data })


    def authorize_payment(self, order=None, amount=None, testing=False):
        """
        Authorize a single payment.

        Returns: ProcessorResult
        """
        if order:
            self.prepare_data(order)
        else:
            order = self.order

        if order.paid_in_full:
            self.log_extra('%s is paid in full, no authorization attempted.',
                           order)
            result = ProcessorResult(self.key, True,
                                      _("No charge needed, paid in full."))
        else:
            self.log_extra('Authorizing payment of %s for %s', amount, order)

            data = self.get_charge_data(amount=balance)
            data['extras'] = [data['address'], data['ship_address'], 
                              data['customer_info'],]

            result = self.send_post(data=data, testing=testing,
                                    post_func=self.send_authorize_post,)

        return result

    def can_authorize(self):
        return True

    #def can_recur_bill(self):
    #    return True

    def capture_authorized_payment(self, authorization, testing=False,
                                   order=None, amount=None):
        """
        Capture a single payment
        """
        if order:
            self.prepare_data(order)
        else:
            order = self.order

        if order.authorized_remaining == Decimal('0.00'):
            self.log_extra('No remaining authorizations on %s', order)
            return ProcessorResult(self.key, True, _("Already complete"))

        self.log_extra('Capturing Authorization #%i for %s',
                       authorization.id, order)
        result = self.send_post(data=authorization.id, testing=testing,
                                post_func=self.send_capture_post,)

        return result

    def capture_payment(self, testing=False, order=None, amount=None):
        """
        Process payments without an authorization step.
        """
        if order:
            self.prepare_data(order)
        else:
            order = self.order

        if order.paid_in_full:
            self.log_extra('%s is paid in full, no capture attempted.', order)
            results = ProcessorResult(self.key, True, _("No charge needed, "
                                                        "paid in full."))
            self.record_payment()
        else:
            self.log_extra('Capturing payment for %s', order)

            data = self.get_charge_data(amount=amount)
            data['extras'] = [data['address'], data['ship_address'], 
                              data['customer_info'],]
            results = self.send_post(data=data, post_func=self.send_sale_post,
                                     testing=testing,)

        return results

    def get_void_auth_data(self, authorization):
        """Build the dictionary needed to process a prior auth release."""
        settings = self.settings
        trans = {
            'authorization' : authorization,
            'amount' : Decimal('0.00'),
        }

        if self.is_live():
            conn = settings.CONNECTION.value
            self.log_extra('Using live connection.')
        else:
            testflag = 'TRUE'
            conn = settings.CONNECTION_TEST.value
            self.log_extra('Using test connection.')

        if self.settings.SIMULATE.value:
            testflag = 'TRUE'
        else:
            testflag = 'FALSE'

        trans['connection'] = conn

        trans['configuration'] = {
            'x_login' : settings.LOGIN.value,
            'x_tran_key' : settings.TRANKEY.value,
            'x_version' : '3.1',
            'x_relay_response' : 'FALSE',
            'x_test_request' : testflag,
            'x_delim_data' : 'TRUE',
            'x_delim_char' : '|',
            'x_type': 'VOID',
            'x_trans_id' : authorization.transaction_id
            }

        self.log_extra('void auth configuration: %s', trans['configuration'])

        postdata = urlencode(trans['configuration'])
        trans['postString'] = postdata

        self.log_extra('void auth poststring: %s', postdata)
        trans['logPostString'] = postdata

        return trans

    def release_authorized_payment(self, order=None, auth=None, testing=False):
        """Release a previously authorized payment."""
        if order:
            self.prepare_data(order)
        else:
            order = self.order

        self.log_extra('Releasing Authorization #%i for %s', auth.id, order)
        data = self.get_void_auth_data(auth)
        results = None
        if data:
            results = self.send_post(data, testing)

        if results.success:
            auth.complete = True
            auth.save()

        return results

    def send_authorize_post(self, data):
        responses, unconsumed_data = self.payflow.authorization(
            credit_card=data['credit_card'], amount=data['amount'],
            extras=data['extras'])
        return responses, unconsumed_data, self.record_authorization

    def send_capture_post(self, authorization_id):
        responses, unconsumed_data = self.payflowpro.capture(authorization.id)
        return responses, unconsumed_data, self.record_payment

    def send_sale_psot(self, data):
        responses, unconsumed_data = self.payflowpro.sale(
            credit_card=data['credit_card'], amount=data['amount'],
            extras=data['extras'])

    def send_post(self, data, post_func, testing=False):
        """
        Execute the post to Authorize Net.

        Params:
        - data: dictionary as returned by get_standard_charge_data
        - testing: if true, then don't record the payment

        Returns:
        - ProcessorResult
        """
        self.log_extra("About to send PayflowPro a request: %s",
                       data['log_string'])
        responses, unconsumed_data, record_function = post_func(data)
        self._handle_unconsumed(unconsumed_data)
        self._log_responses(rseponses)

        response = responses[0]
        success = response.result == 0
        if success:
            # success!
            self.log.info("successful %s for order #%d",
                          post_func.__name__, order.id)
            transaction_id = response.pnref
            response_text = response.respmsg
            reason_code = response.result
            if not testing:
                self.log_extra("Success, calling %s", record_function.__name__)
                payment = record_function(
                    order=order, amount=balance,
                    transaction_id=transaction_id, reason_code=reason_code)
        else:
            # failure =(
            self.log.info("failed %s for order #%d",
                          post_func.__name__, order.id)
            if not testing:
                payment = self.record_failure(
                    amount=amount, transaction_id=transaction_id,
                    reason_code=reason_code, details=response_text)
                
        self.log_extra("Returning success=%s, reason=%s, response_text=%s",
                       success, reason_code, response_text)

        return ProcessorResult(self.key, success, response_text,
                                 payment=payment)


if __name__ == "__main__":
    """
    This is for testing - enabling you to run from the command line and make
    sure everything is ok
    """
    import os
    from livesettings import config_get_group

    # Set up some dummy classes to mimic classes being passed through Satchmo
    class testContact(object):
        pass
    class testCC(object):
        pass
    class testOrder(object):
        def __init__(self):
            self.contact = testContact()
            self.credit_card = testCC()
        def order_success(self):
            pass

    if not os.environ.has_key("DJANGO_SETTINGS_MODULE"):
        os.environ["DJANGO_SETTINGS_MODULE"]="satchmo_store.settings"

    settings_module = os.environ['DJANGO_SETTINGS_MODULE']
    settingsl = settings_module.split('.')
    settings = __import__(settings_module, {}, {}, settingsl[-1])

    sampleOrder = testOrder()
    sampleOrder.contact.first_name = 'Chris'
    sampleOrder.contact.last_name = 'Smith'
    sampleOrder.contact.primary_phone = '801-555-9242'
    sampleOrder.full_bill_street = '123 Main Street'
    sampleOrder.bill_postal_code = '12345'
    sampleOrder.bill_state = 'TN'
    sampleOrder.bill_city = 'Some City'
    sampleOrder.bill_country = 'US'
    sampleOrder.total = "27.01"
    sampleOrder.balance = "27.01"
    sampleOrder.credit_card.decryptedCC = '6011000000000012'
    sampleOrder.credit_card.expirationDate = "10/11"
    sampleOrder.credit_card.ccv = "144"

    authorize_settings = config_get_group('PAYMENT_AUTHORIZENET')
    if authorize_settings.LIVE.value:
        print "Warning.  You are submitting a live order.  AUTHORIZE.NET system is set LIVE."

    processor = PaymentProcessor(authorize_settings)
    processor.prepare_data(sampleOrder)
    results = processor.process(testing=True)
    print results


