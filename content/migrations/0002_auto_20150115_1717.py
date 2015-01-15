# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='body_sr_latn',
            field=models.TextField(null=True, verbose_name='Body', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='content',
            name='slug_sr_latn',
            field=models.SlugField(max_length=100, null=True, verbose_name='Slug'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='content',
            name='title_sr_latn',
            field=models.CharField(max_length=100, null=True, verbose_name='Title'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='category',
            name='active',
            field=models.BooleanField(default=True, verbose_name='aktivan'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, verbose_name='ime'),
            preserve_default=True,
        ),
    ]
