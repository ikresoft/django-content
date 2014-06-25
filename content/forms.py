#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.conf import settings

from .models import Content
from taggit.models import Tag
from django_select2.fields import AutoModelSelect2TagField

WIDGET_ATTRS = {'size': '85'}

class TagField(AutoModelSelect2TagField):
    queryset = Tag.objects
    search_fields = ['name__icontains', ]

    def get_model_field_values(self, value):
        return {'name': value}

class ContentForm(forms.ModelForm):
    if 'taggit' in settings.INSTALLED_APPS:
       tags = TagField(required=False)

    non_staff_author = forms.CharField(
        widget=forms.TextInput(attrs=WIDGET_ATTRS),
        help_text=_('An HTML-formatted rendering of the author(s) not on staff.'),
        max_length=200,
        required=False)

    class Meta:
        model = Content
        widgets = {
            'title': forms.TextInput(attrs={'size': '100', 'style': 'width=100%;'})
        }

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        instance = kwargs.get('instance', None)

        if not instance and not 'site' in initial:
            initial['site'] = (Site.objects.get_current().id, )

        if instance is not None:
            initial['tags'] = instance.tags.all()
        kwargs.update({'initial': initial})
        super(ContentForm, self).__init__(*args, **kwargs)
