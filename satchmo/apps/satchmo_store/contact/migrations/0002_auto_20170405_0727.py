# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='user',
            field=models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
