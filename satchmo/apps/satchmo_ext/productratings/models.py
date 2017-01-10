from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
if 'django_comments' in settings.INSTALLED_APPS:
    from django_comments.models import Comment
    from django_comments.signals import comment_was_posted
else:
    from django.contrib.comments.models import Comment
    from django.contrib.comments.signals import comment_was_posted
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

from .listeners import save_rating, one_rating_per_product, check_with_akismet
comment_was_posted.connect(save_rating, sender=Comment)
comment_was_posted.connect(one_rating_per_product, sender=Comment)
comment_was_posted.connect(check_with_akismet, sender=Comment)
