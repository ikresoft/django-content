# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_auto_20150727_0855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorycontent',
            name='categories',
            field=models.ManyToManyField(to='content.Category', blank=True),
        ),
        migrations.AlterField(
            model_name='content',
            name='authors',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Authors', blank=True),
        ),
    ]
