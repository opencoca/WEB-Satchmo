from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings
from livesettings import config_value
from sorl.thumbnail.admin import AdminImageMixin
from sorl.thumbnail import get_thumbnail

class AdminImageWithThumbnailWidget(AdminImageMixin, forms.FileInput):
    """
    A FileField Widget that shows its current image as a thumbnail if it has one.
    """
    def __init__(self, attrs={}):
        super(AdminImageWithThumbnailWidget, self).__init__(attrs)
        
    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "path"):
            if value.path.startswith(settings.MEDIA_ROOT):
                image = value.path[len(settings.MEDIA_ROOT):]
            else:
                image = value.path
            # Generate 120px wide thumbnail for the admin interface
            # TODO: replace manual thumbnail generation with a template tag
            thumb = get_thumbnail(image, '120',
                    quality=config_value('THUMBNAIL', 'IMAGE_QUALITY'))
            output.append('<img src="%s" /><br/>%s<br/> %s ' % \
                (thumb.url, value.url, _('Change:')))
        output.append(super(AdminImageWithThumbnailWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
