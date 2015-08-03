# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name_de_ch',
            field=models.CharField(max_length=100, null=True, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='category',
            name='name_fr_ch',
            field=models.CharField(max_length=100, null=True, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='category',
            name='slug_de_ch',
            field=models.SlugField(null=True, verbose_name='slug'),
        ),
        migrations.AddField(
            model_name='category',
            name='slug_fr_ch',
            field=models.SlugField(null=True, verbose_name='slug'),
        ),
        migrations.AddField(
            model_name='content',
            name='body_de_ch',
            field=models.TextField(null=True, verbose_name='Body', blank=True),
        ),
        migrations.AddField(
            model_name='content',
            name='body_fr_ch',
            field=models.TextField(null=True, verbose_name='Body', blank=True),
        ),
        migrations.AddField(
            model_name='content',
            name='slug_de_ch',
            field=models.SlugField(max_length=100, null=True, verbose_name='K\xfcrzel'),
        ),
        migrations.AddField(
            model_name='content',
            name='slug_fr_ch',
            field=models.SlugField(max_length=100, null=True, verbose_name='K\xfcrzel'),
        ),
        migrations.AddField(
            model_name='content',
            name='title_de_ch',
            field=models.CharField(max_length=100, null=True, verbose_name='Titel'),
        ),
        migrations.AddField(
            model_name='content',
            name='title_fr_ch',
            field=models.CharField(max_length=100, null=True, verbose_name='Titel'),
        ),
        migrations.AlterField(
            model_name='category',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Aktiv'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='content',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_content.content_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AlterField(
            model_name='content',
            name='site',
            field=models.ManyToManyField(to='sites.Site', verbose_name='Seiten'),
        ),
        migrations.AlterField(
            model_name='content',
            name='slug',
            field=models.SlugField(max_length=100, verbose_name='K\xfcrzel'),
        ),
        migrations.AlterField(
            model_name='content',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Titel'),
        ),
    ]
