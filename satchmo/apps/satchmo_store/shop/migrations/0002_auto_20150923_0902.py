# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderauthorization',
            name='payment',
            field=models.CharField(blank=True, max_length=25, verbose_name='Payment Method', choices=[('AUTHORIZENET', 'Credit Cards'), ('PURCHASEORDER', 'Purchase Order'), ('GIFTCERTIFICATE', 'Gift Certificate'), ('DUMMY', 'Payment test module')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='payment',
            field=models.CharField(blank=True, max_length=25, verbose_name='Payment Method', choices=[('AUTHORIZENET', 'Credit Cards'), ('PURCHASEORDER', 'Purchase Order'), ('GIFTCERTIFICATE', 'Gift Certificate'), ('DUMMY', 'Payment test module')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderpaymentfailure',
            name='payment',
            field=models.CharField(blank=True, max_length=25, verbose_name='Payment Method', choices=[('AUTHORIZENET', 'Credit Cards'), ('PURCHASEORDER', 'Purchase Order'), ('GIFTCERTIFICATE', 'Gift Certificate'), ('DUMMY', 'Payment test module')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderpendingpayment',
            name='payment',
            field=models.CharField(blank=True, max_length=25, verbose_name='Payment Method', choices=[('AUTHORIZENET', 'Credit Cards'), ('PURCHASEORDER', 'Purchase Order'), ('GIFTCERTIFICATE', 'Gift Certificate'), ('DUMMY', 'Payment test module')]),
            preserve_default=True,
        ),
    ]
