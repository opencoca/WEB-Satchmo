from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
if 'django_comments' in settings.INSTALLED_APPS:
    from django_comments.models import Comment    
else:
    from django.contrib.comments.models import Comment
from satchmo_utils.signals import collect_urls
import product
import satchmo_store

class ProductRating(models.Model):
    """A rating attached to a comment"""
    comment = models.OneToOneField(Comment, verbose_name="Rating", primary_key=True)
    rating = models.IntegerField(_("Rating"))

import config
from urls import add_product_urls, add_comment_urls
collect_urls.connect(add_product_urls, sender=product)
collect_urls.connect(add_comment_urls, sender=satchmo_store)
