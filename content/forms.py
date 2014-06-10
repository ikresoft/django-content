#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from django import forms
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

from modeltranslation.forms import TranslationModelForm

from .models import Content

WIDGET_ATTRS = {'size': '85'}

class SlugMixin(object):

    def clean_slug(self):
        """The slug + the date_modified must be unique together"""

        if 'date_modified' in self.cleaned_data:
            date_modified = self.cleaned_data['date_modified']
            try:
                Content.objects.get(
                    slug=self.cleaned_data['slug'],
                    date_modified__year=date_modified.year,
                    date_modified__month=date_modified.month,
                    date_modified__day=date_modified.day)
                raise forms.ValidationError(
                    'Please enter a different slug. The one you'\
                    'entered is already being used for {0}'.format(
                         date_modified.strftime("%Y-%b-%d")))
            except Content.DoesNotExist:
                pass

        return self.cleaned_data['slug']

class ContentForm(TranslationModelForm):

    title = forms.CharField(
        widget=forms.TextInput(attrs=WIDGET_ATTRS),
        max_length=100)
    non_staff_author = forms.CharField(
        widget=forms.TextInput(attrs=WIDGET_ATTRS),
        help_text=_('An HTML-formatted rendering of the author(s) not on staff.'),
        max_length=200,
        required=False)

    class Meta:
        model = Content

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        instance = kwargs.get('instance', None)

        if not instance and not 'site' in initial:
            initial['site'] = (Site.objects.get_current().id, )

        kwargs.update({'initial': initial})
        super(ContentForm, self).__init__(*args, **kwargs)
