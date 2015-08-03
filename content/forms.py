#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.conf import settings
from content import settings as app_settings

from .models import Content, Category, CategoryContent
from taggit.models import Tag
from django_select2.fields import AutoModelSelect2TagField
from widgets import MpttTreeWidget

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
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        instance = kwargs.get('instance', None)

        if not instance and 'site' not in initial:
            initial['site'] = (Site.objects.get_current().id, )

        if instance is not None:
            initial['tags'] = instance.tags.all()
        kwargs.update({'initial': initial})
        super(ContentForm, self).__init__(*args, **kwargs)


class CategoryContentForm(ContentForm):
    categories = forms.ModelMultipleChoiceField(required=True, queryset=Category.objects.all(), widget=MpttTreeWidget)

    class Meta:
        model = CategoryContent
        fields = '__all__'


class CategoryAdminForm(forms.ModelForm):

    # def clean_slug(self):
    #     slug = ('slug_' + get_language().replace('-', '_')) if settings.USE_TRANSLATION else 'slug'
    #     if self.cleaned_data[slug] is not None:
    #         if self.instance is None:
    #             self.cleaned_data[slug] = slugify(SLUG_TRANSLITERATOR(self.cleaned_data['name']))
    #     return self.cleaned_data['slug'][:50]

    def clean(self):

        super(CategoryAdminForm, self).clean()
        slug = ('slug_' + get_language().replace('-', '_')) if app_settings.USE_TRANSLATION else 'slug'
        if not self.is_valid():
            return self.cleaned_data

        opts = self._meta

        # Validate slug is valid in that level
        kwargs = {}
        if self.cleaned_data.get('parent', None) is None:
            kwargs['parent__isnull'] = True
        else:
            kwargs['parent__pk'] = int(self.cleaned_data['parent'].id)
        this_level_slugs = [c['slug'] for c in opts.model.objects.filter(
                                **kwargs).values('id', 'slug'
                                ) if c['id'] != self.instance.id]
        if self.cleaned_data[slug] in this_level_slugs:
            raise forms.ValidationError(_('The slug must be unique among '
                                          'the items at its level.'))

        # Validate Category Parent
        # Make sure the category doesn't set itself or any of its children as
        # its parent.
        if self.instance.id:
            decendant_ids = self.instance.get_descendants().values_list('id', flat=True)
        if self.cleaned_data.get('parent', None) is None or self.instance.id is None:
            return self.cleaned_data
        elif self.cleaned_data['parent'].id == self.instance.id:
            raise forms.ValidationError(_("You can't set the parent of the "
                                          "item to itself."))
        elif self.instance.id and self.cleaned_data['parent'].id in decendant_ids:
            raise forms.ValidationError(_("You can't set the parent of the "
                                          "item to a descendant."))
        return self.cleaned_data

    class Meta:
        model = Category
        fields = '__all__'
