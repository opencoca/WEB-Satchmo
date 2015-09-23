# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
        ('l10n', '0001_initial'),
        ('area', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxrate',
            name='taxClass',
            field=models.ForeignKey(verbose_name='Tax Class', to='product.TaxClass'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taxrate',
            name='taxCountry',
            field=models.ForeignKey(verbose_name='Tax Country', blank=True, to='l10n.Country', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taxrate',
            name='taxZone',
            field=models.ForeignKey(verbose_name='Tax Zone', blank=True, to='l10n.AdminArea', null=True),
            preserve_default=True,
        ),
    ]
