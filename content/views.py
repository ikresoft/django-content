#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import EmptyPage, InvalidPage
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.views.generic import (ArchiveIndexView, YearArchiveView,
    MonthArchiveView, WeekArchiveView, DayArchiveView, TodayArchiveView,
    DateDetailView)

from content import settings
from .models import Content
from .paragraph_paginator import ParagraphPaginator

@staff_member_required
def admin_changeset_list(request, content_id,
    template_name='admin/content/changesets.html'):
    try:
        content = Content.objects.get(pk=content_id)
    except Content.DoesNotExist:
        raise Http404

    chsets = content.changeset_set.all().order_by('-revision')

    return render_to_response(template_name,
                              {'content': content,
                               'changesets': chsets},
                              context_instance=RequestContext(request))


@staff_member_required
def admin_changeset_revert(request, story_id, revision_id,
    template_name='admin/content/changeset_revert.html'):

    try:
        story = Story.objects.get(pk=story_id)
    except Story.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        if 'confirm' in request.POST:
            story.revert_to(revision_id)
            return HttpResponseRedirect('../../')
        elif 'cancel' in request.POST:
            return HttpResponseRedirect('../../changesets/')

    changeset = story.changeset_set.get(revision=revision_id)

    return render_to_response(template_name,
                              {'story': story,
                               'changeset': changeset},
                              context_instance=RequestContext(request))


