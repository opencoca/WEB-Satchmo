# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import satchmo_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionProduct',
            fields=[
                ('product', models.OneToOneField(primary_key=True, serialize=False, to='product.Product', verbose_name='Product')),
                ('recurring', models.BooleanField(default=False, help_text='Customer will be charged the regular product price on a periodic basis.', verbose_name='Recurring Billing')),
                ('recurring_times', models.IntegerField(help_text='Number of payments which will occur at the regular rate.  (optional)', null=True, verbose_name='Recurring Times', blank=True)),
                ('expire_length', models.IntegerField(help_text='Length of each billing cycle', null=True, verbose_name='Duration', blank=True)),
                ('expire_unit', models.CharField(default=b'DAY', max_length=5, verbose_name='Expire Unit', choices=[(b'DAY', 'Days'), (b'MONTH', 'Months')])),
                ('is_shippable', models.IntegerField(help_text='Is this product shippable?', max_length=1, verbose_name='Shippable?', choices=[(0, 'No Shipping Charges'), (1, 'Pay Shipping Once'), (2, 'Pay Shipping Each Billing Cycle')])),
            ],
            options={
                'verbose_name': 'Subscription Product',
                'verbose_name_plural': 'Subscription Products',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', satchmo_utils.fields.CurrencyField(help_text='Set to 0 for a free trial.  Leave empty if product does not have a trial.', null=True, verbose_name='Price', max_digits=10, decimal_places=2)),
                ('expire_length', models.IntegerField(help_text='Length of trial billing cycle.  Leave empty if product does not have a trial.', null=True, verbose_name='Trial Duration', blank=True)),
                ('subscription', models.ForeignKey(to='subscription.SubscriptionProduct')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'Trial Terms',
                'verbose_name_plural': 'Trial Terms',
            },
            bases=(models.Model,),
        ),
    ]
