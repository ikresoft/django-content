# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import mptt.fields
import taggit.managers
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='content.Category', null=True)),
            ],
            options={
                'ordering': ('tree_id', 'lft'),
                'abstract': False,
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('body', models.TextField(null=True, verbose_name='Body', blank=True)),
                ('slug', models.SlugField(max_length=100, verbose_name='Slug')),
                ('non_staff_author', models.CharField(help_text='An HTML-formatted rendering of an author(s) not on staff.', max_length=200, null=True, verbose_name='Non-staff author(s)', blank=True)),
                ('date_modified', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Date modified', blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('password', models.CharField(max_length=20, null=True, blank=True)),
                ('private', models.BooleanField(default=False)),
                ('allow_comments', models.BooleanField(default=True, verbose_name='Allow comments')),
                ('status', models.IntegerField(default=1, verbose_name='Published Status', choices=[(1, 'DRAFT'), (2, 'READY FOR EDITING'), (3, 'READY TO PUBLISH'), (4, 'PUBLISHED'), (5, 'REJECTED'), (6, 'UN-PUBLISHED')])),
                ('origin', models.IntegerField(default=0, verbose_name='Origin', choices=[(0, 'Admin')])),
            ],
            options={
                'ordering': ['-date_modified'],
                'get_latest_by': 'date_modified',
                'verbose_name': 'content',
                'verbose_name_plural': 'Contents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryContent',
            fields=[
                ('content_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='content.Content')),
                ('allow_pings', models.BooleanField(default=True, verbose_name='Allow pings')),
                ('is_sticky', models.BooleanField(default=False)),
                ('categories', models.ManyToManyField(to='content.Category', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
        migrations.AddField(
            model_name='content',
            name='authors',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, verbose_name='Authors', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='content',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_content.content_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='content',
            name='site',
            field=models.ManyToManyField(to='sites.Site', verbose_name='Sites'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='content',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='content',
            unique_together=set([('date_modified', 'slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('parent', 'name')]),
        ),
    ]
