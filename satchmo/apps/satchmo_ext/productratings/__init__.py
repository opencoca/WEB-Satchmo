try:
    from django.contrib.comments.models import Comment
    from django.contrib.comments.signals import comment_was_posted
except ImportError:
    from django_comments.models import Comment
    from django_comments.signals import comment_was_posted
from .listeners import save_rating, one_rating_per_product, check_with_akismet

comment_was_posted.connect(save_rating, sender=Comment)
comment_was_posted.connect(one_rating_per_product, sender=Comment)
comment_was_posted.connect(check_with_akismet, sender=Comment)
