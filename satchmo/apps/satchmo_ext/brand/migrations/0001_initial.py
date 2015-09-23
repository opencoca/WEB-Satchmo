# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import satchmo_utils.thumbnail.field
import l10n.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='Used for URLs', unique=True, verbose_name='Slug')),
                ('ordering', models.IntegerField(verbose_name='Ordering')),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('ordering', 'slug'),
                'verbose_name': 'Brand',
                'verbose_name_plural': 'Brands',
            },
            bases=(models.Model, l10n.mixins.TranslatedObjectMixin),
        ),
        migrations.CreateModel(
            name='BrandCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='Used for URLs', verbose_name='Slug')),
                ('ordering', models.IntegerField(verbose_name='Ordering')),
                ('active', models.BooleanField(default=True)),
                ('brand', models.ForeignKey(related_name='categories', to='brand.Brand')),
            ],
            options={
                'ordering': ('ordering', 'slug'),
                'verbose_name': 'Brand Category',
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model, l10n.mixins.TranslatedObjectMixin),
        ),
        migrations.CreateModel(
            name='BrandCategoryProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('brandcategory', models.ForeignKey(to='brand.BrandCategory')),
                ('product', models.ForeignKey(to='product.Product')),
            ],
            options={
                'verbose_name': 'Brand Category Product',
                'verbose_name_plural': 'Brand Category Products',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BrandCategoryTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')])),
                ('name', models.CharField(max_length=100, verbose_name='title')),
                ('short_description', models.CharField(max_length=200, verbose_name='Short Description', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('picture', satchmo_utils.thumbnail.field.ImageWithThumbnailField(max_length=200, null=True, upload_to=satchmo_utils.thumbnail.field.upload_dir, blank=True)),
                ('brandcategory', models.ForeignKey(related_name='translations', to='brand.BrandCategory')),
            ],
            options={
                'ordering': ('languagecode',),
                'verbose_name_plural': 'Brand Category Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BrandProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('brand', models.ForeignKey(to='brand.Brand')),
                ('product', models.ForeignKey(to='product.Product')),
            ],
            options={
                'verbose_name': 'Brand Product',
                'verbose_name_plural': 'Brand Products',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BrandTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')])),
                ('name', models.CharField(max_length=100, verbose_name='title')),
                ('short_description', models.CharField(max_length=200, verbose_name='Short Description', blank=True)),
                ('description', models.TextField(verbose_name='Full Description', blank=True)),
                ('picture', satchmo_utils.thumbnail.field.ImageWithThumbnailField(max_length=200, null=True, upload_to=satchmo_utils.thumbnail.field.upload_dir, blank=True)),
                ('brand', models.ForeignKey(related_name='translations', to='brand.Brand')),
            ],
            options={
                'ordering': ('languagecode',),
                'verbose_name': 'Brand Translation',
                'verbose_name_plural': 'Brand Translations',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='brandcategory',
            name='products',
            field=models.ManyToManyField(to='product.Product', verbose_name='Products', through='brand.BrandCategoryProduct', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brand',
            name='products',
            field=models.ManyToManyField(to='product.Product', verbose_name='Products', through='brand.BrandProduct', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brand',
            name='site',
            field=models.ForeignKey(to='sites.Site'),
            preserve_default=True,
        ),
    ]
