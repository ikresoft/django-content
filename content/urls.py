#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""URL definitions for posts
"""
try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url

from views import CategoryContentListView, CategoryContentDetailView

urlpatterns = patterns('',
    # post detail
    url(
        r'^category/(?P<path>.+)/(?P<slug>[-\w]+)/$',
        CategoryContentDetailView.as_view(),
        name='category_content_detail'
    ),

    # news archive index
    url(
        r'^category/(?P<path>.+)/$',
        CategoryContentListView.as_view(),
        name='category_content_list'
    ),
)
