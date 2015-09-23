# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_creditcarddetail_orderpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentoption',
            name='optionName',
            field=models.CharField(help_text='The class name as defined in payment.py', unique=True, max_length=20, verbose_name='Option Name', choices=[('AUTHORIZENET', 'Credit Cards'), ('PURCHASEORDER', 'Purchase Order'), ('GIFTCERTIFICATE', 'Gift Certificate'), ('DUMMY', 'Payment test module')]),
            preserve_default=True,
        ),
    ]
