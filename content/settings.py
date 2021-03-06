#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provides the default settings for the news app
"""

import warnings

from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

DEFAULT_STATUS_CHOICES = (
    (1, _(u'DRAFT')),
    (2, _(u'READY FOR EDITING')),
    (3, _(u'READY TO PUBLISH')),
    (4, _(u'PUBLISHED')),
    (5, _(u'REJECTED')),
    (6, _(u'UN-PUBLISHED')),
)

DEFAULT_ORIGIN_CHOICES = (
    (0, _(u'Admin')),
)

DEFAULT_PAGINATION = {
    'PAGINATE': False,
    'P_PER_PAGE': 20,
    'ORPHANS': 4
}
DEFAULT_QUICKEDIT_FIELDS = (
    'title',
    'slug',
    'password',
    'private',
    'tags',
)

DEFAULT_SETTINGS = {
    'AUTHOR_MODEL': settings.AUTH_USER_MODEL,
    'AUTHOR_MODEL_LIMIT_CHOICES': {'is_staff': True},
    'DEFAULT_ORIGIN': 0,
    'DEFAULT_STATUS': 1,
    'ADMIN_EXTRAS': {
        'EXTRA_FIELDSETS': (),
        'RAW_ID_FIELDS': (),
        'FILTER_HORIZONTAL_FIELDS': ('authors',),
        'SEARCH_FIELDS': ('title',),
        'LIST_PER_PAGE': 25,
        'CHILD_MODELS': [],
    },
    'ORDERING': ['-date_modified'],
    'ORIGIN_CHOICES': DEFAULT_ORIGIN_CHOICES,
    'PAGINATION': DEFAULT_PAGINATION,
    'PUBLISHED_STATUS': 4,
    'QUICKEDIT_FIELDS': DEFAULT_QUICKEDIT_FIELDS,
    'RELATION_MODELS': [],
    'STATUS_CHOICES': DEFAULT_STATUS_CHOICES,
    'THROW_404': True,
    'USE_REVERSION': False,
    'USE_TRANSLATION': 'modeltranslation' in settings.INSTALLED_APPS and settings.USE_I18N,
    'WIDGET': 'ckeditor.widgets.CKEditorWidget',
    'WIDGET_PARAMS': {"config_name": "content"},
    'WIDGET_ATTRS': None,
    'WIDGET_FIELDS': ['body', ]
}

USER_SETTINGS = getattr(settings, 'CONTENT_SETTINGS', {})
CKEDITOR_SETTINGS = getattr(settings, 'CKEDITOR_CONFIGS', {})
CONTENT_CKEDITOR_SETTINGS = getattr(settings, 'CONTENT_CKEDITOR_CONFIGS', {})

DEFAULT_SETTINGS.update(USER_SETTINGS)
CKEDITOR_SETTINGS.update({
    "content": {
        'toolbar_Content': [
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', 'Undo', 'Redo', 'SelectAll'],
            ['Paragraph', 'Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', 'RemoveFormat', 'WPMore'], ['Source'],
            ['Image', 'Youtube', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'Iframe'], ['NumberedList', 'BulletedList', 'Outdent', 'Indent', 'Blockquote',
            'CreateDiv', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'], ['Link', 'Unlink', 'Anchor'],
            ['TextColor', 'BGColor'], ['Maximize', 'ShowBlocks'],
        ],
        'toolbar': 'Content',
        'height': 300,
        'width': '100%',
        'filebrowserBrowseUrl': "/url-browser/form-view/?_popup=1",
        'filebrowserUploadUrl': None,
        'extraPlugins': 'youtube,wpmore',
    }
})

CKEDITOR_SETTINGS.update(CONTENT_CKEDITOR_SETTINGS)

RELATIONS = [Q(app_label=al, model=m) for al, m in [x.split('.') for x in DEFAULT_SETTINGS['RELATION_MODELS']]]

globals().update(DEFAULT_SETTINGS)
globals().update({'RELATIONS': RELATIONS})
