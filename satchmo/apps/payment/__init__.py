def active_gateways():
    """Get a list of activated payment gateways, in the form of
    [(module, config module name),...]
    """
    try:
        from django.apps import apps
        gateways = []
        app_configs = apps.get_app_configs()
        for app_config in app_configs:
            if app_config.models_module is not None and hasattr(app_config.models_module, 'PAYMENT_PROCESSOR'):
                parts = app_config.models_module.__name__.split('.')[:-1]
                module = ".".join(parts)
                group = 'PAYMENT_%s' % parts[-1].upper()
                gateways.append((module, group))
        return gateways
    except ImportError:                
        from django.db import models
        gateways = []
        for app in models.get_apps():
            if hasattr(app, 'PAYMENT_PROCESSOR'):
                parts = app.__name__.split('.')[:-1]
                module = ".".join(parts)
                group = 'PAYMENT_%s' % parts[-1].upper()
                gateways.append((module, group))
        return gateways
