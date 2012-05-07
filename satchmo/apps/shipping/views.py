 # pylint: disable=W0613,W0231
import os
import logging
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_str
from django.utils.importlib import import_module
from django.views.decorators.cache import never_cache
from satchmo_store.shop.models import Order
from satchmo_store.shop.models import Config
from livesettings import config_value


class ConverterError(Exception):
    """An error occurred while setting up the converter
    """


class DocumentBase(object):
    """The base document converter class.

    Any custom-defined converter must subclass this one as the first class.
    """

    def get_context(self, request, order_id, doc):
        order = get_object_or_404(Order, pk=order_id)
        shopDetails = Config.objects.get_current()
        icon_uri = config_value('SHOP', 'LOGO_URI')
        context = {
            'doc': doc,
            'iconURI' : icon_uri,
            'shopDetails' : shopDetails,
            'order' : order,
            'default_view_tax': config_value('TAX','DEFAULT_VIEW_TAX')
        }
        return context

    def __call__(self, request, order_id, doc):
        return self.render(
            request,
            self.get_context(request, order_id, doc)
        )


class RMLTemplateMixin(object):
    """The RML template mixin.

    Subclass from this mixin to load RML templates.
    """

    def get_template(self, request, context):
        template_name = "%s.rml" % context['doc']
        template_path = os.path.join('shop/docs/rml', template_name)
        return loader.get_template(template_path)


class HTMLTemplateMixin(object):
    """The HTML template mixin.

    Subclass from this mixin to load HTML templates.
    """

    def get_template(self, request, context):
        template_name = "%s.html" % context['doc']
        template_path = os.path.join('shop/docs/html', template_name)
        return loader.get_template(template_path)


class HTMLRenderMixin(object):
    """The HTML (normal page) template mixin.

    Subclass from this mixin if you want to render directly within the
    browser.
    """

    def render(self, request, context):
        template = self.get_template(request, context)
        return HttpResponse(template.render(RequestContext(request, context)))


class FileRenderMixin(object):
    """The file render mixin.

    Renders as a downloadable file (attachment). Subclass from this mixin if
    you are not rendering to a format understood by the browser natively.
    """

    def render(self, request, context):
        template = self.get_template(request, context)
        filename = self.get_filename(request, context)
        content = self.convert(
            template.render(RequestContext(request, context))
        )
        response = HttpResponse(mimetype=self.mimetype)
        if config_value('SHIPPING','DOWNLOAD_PDFS'):
            content_disposition = 'attachment; filename=%s' % filename
            response['Content-Disposition'] = content_disposition
        response.write(content)
        return response


class HTMLDocument(DocumentBase, HTMLTemplateMixin, HTMLRenderMixin):
    """The default document class, rendering every document as HTML
    """


class TRMLDocument(DocumentBase, RMLTemplateMixin, FileRenderMixin):
    """The RML PDF document generator.

    Available only if trml2pdf is installed.
    """

    mimetype = "application/pdf"

    def __init__(self):
        try:
            import trml2pdf
        except ImportError:
            raise ConverterError(
                "'trml2pdf' must be installed on your system "
                "for the TRMLDocument converter to work properly. "
                "Please make sure "
                "that the 'trml2pdf' egg is within your PYTHONPATH, "
                "and install it via 'pip install trml2pdf' otherwise."
            )
        self._converter = (trml2pdf.parseString,)

    def get_filename(self, request, context):
        return '%s-%s-%d.pdf' % (
            context['shopDetails'].domain,
            context['doc'],
            context['order'].pk
        )

    def convert(self, data):
        return self._converter[0](smart_str(data))


class WKHTMLDocument(DocumentBase, HTMLTemplateMixin, FileRenderMixin):
    """The "webkit to html" PDF generator.

    Available only if the static binary of
    http://code.google.com/p/wkhtmltopdf/ has been downloaded and extracted
    somewhere and its path provided via 'settings.py', as follows:

    SATCHMO_SETTINGS = {
        ...
        'WKHTML2PDF_BINARIES': {
            ...
            'linux2': '/path/to/wkhtmltopdf'
        }
    }

    It is to be noted that every key value pair within 'WKHTML2PDF_BINARIES'
    associates a different executable to every platform as named by
    'sys.platform'. You can have many or just one, depending if you reuse your
    'settings.py' between development and production (and whether you use Mac
    OS X for development).
    """

    mimetype = "application/pdf"

    def __init__(self):
        import sys
        satchmo_settings = getattr(settings, 'SATCHMO_SETTINGS', {})
        wkhtml2pdf_binaries = satchmo_settings.get(
            'WKHTML2PDF_BINARIES',
            {}
        )
        self.wkhtml2pdf = wkhtml2pdf_binaries.get(sys.platform, None)
        if self.wkhtml2pdf is None:
            raise ConverterError(
                ("WKHTMLDocument can't find the 'wkhtmltopdf' binary "
                 "for your platform. "
                 "Please make sure "
                 "that SATCHMO_SETTINGS['WKHTML2PDF_BINARIES']['%s'] exists "
                 "within your 'settings.py' "
                 "and that it contains the absolute path to the binary.") % (
                    sys.platform,
                )
            )

    def get_filename(self, request, context):
        return '%s-%s-%d.pdf' % (
            context['shopDetails'].domain,
            context['doc'],
            context['order'].pk
        )

    def convert(self, data):
        import subprocess
        logger = logging.getLogger('wkhtml2pdf')
        if isinstance(data, unicode):
            data = data.encode("utf-8")
        args = (self.wkhtml2pdf, "-q", "--encoding", "utf-8",
                "--print-media-type", "-", "-")
        process = subprocess.Popen(
            args,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        logger.debug("Calling %s" % " ".join(args))
        stdout, stderr = process.communicate(data)
        if process.returncode != 0:
            logger.error("wkhtmltopdf failed (%d): %s" % (process.returncode,
                                                          stderr))
        return stdout


@staff_member_required
@never_cache
def displayDoc(request, id, doc):
    """Tries to load the converted specified in the
    SATCHMO_SETTINGS['DOCUMENT_CONVERTER'] setting (as the full dotted name of
    the class).

    If this setting is absent, defaults to using HTMLDocument.
    """
    Converter = getattr(settings, 'SATCHMO_SETTINGS', {}).get(
        'DOCUMENT_CONVERTER', None)
    if Converter is None:
        Converter = HTMLDocument
    else:
        module_name, class_name = Converter.rsplit('.', 1)
        module = import_module(module_name)
        Converter = getattr(module, class_name)
    converter = Converter()
    return converter(request, id, doc)
