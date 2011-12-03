import shipper
from livesettings import config_choice_values, config_get_group
from fedex.config import FedexConfig
import logging

log = logging.getLogger('fedex_web_service.shipper')

def get_methods():
    settings = config_get_group('shipping.modules.fedex_web_services')
    if not settings.ACCOUNT.value:
        log.warn("No fedex account found in settings")
        return

    if not settings.METER_NUMBER.value:
        log.warn("No fedex meter number found in settings")
        return

    if not settings.AUTHENTICATION_KEY.value:
        log.warn("No fedex authentication key found in settings")
        return

    if not settings.AUTHENTICATION_PASSWORD.value:
        log.warn("No fedex authentication password found in settings")
        return
        
    if not settings.PACKAGING.value:
        packaging = "YOUR_PACKAGING"
    else:
        packaging = settings.PACKAGING.value
    if not settings.DEFAULT_ITEM_WEIGHT.value:
        default_weight = 0.5
    else:
        default_weight = settings.DEFAULT_ITEM_WEIGHT.value
    CONFIG_OBJ = FedexConfig(key=settings.AUTHENTICATION_KEY.value,
                         password=settings.AUTHENTICATION_PASSWORD.value,
                         account_number=settings.ACCOUNT.value,
                         meter_number=settings.METER_NUMBER.value,
                         express_region_code=settings.SHIPPER_REGION.value,
                         use_test_server=settings.TEST_SERVER.value)

    return [shipper.Shipper(service_type=value, config=CONFIG_OBJ, packaging=packaging, default_weight = default_weight) for value in config_choice_values('shipping.modules.fedex_web_services', 'SHIPPING_CHOICES')]
