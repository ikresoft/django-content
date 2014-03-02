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


def content_detail(request, year, month, day, slug,
        p_per_page=settings.PAGINATION['P_PER_PAGE'],
        orphans=settings.PAGINATION['ORPHANS'],
        p_object_name="story_content", template_object_name="story",
        template_name="content/pag_story.html", extra_context={}):
    """
    A detail view for contents that can paginates the story by paragraph.
    If a story is not found a 404 or a custom template can be rendered
    by setting `THROW_404` to `False`.

    By default, template `contents/pag_story.html` is used to render the
    story which expects the story to be paginated by paragraphs. If the
    paragraph paginator is not used, the template `contents/story_detail.html`
    is used to render the story.

    There is two main variables passed to the template `p_object_name`, which
    is the contents body field, and `template_object_name` which is the
    story instance it self.

    Argument List:

    * **year** - Four digets, `2012`, `1997`, `2004`
    * **month** - `jul` `jan` `aug`
    * **day** - Two digits, `01` `23`, `31`
    * **slug** - slugified string, `this-is-a-slug`
    * **p_per_page** - pagination setting, paragraphs per page
    * **orphans** - pagination setting, number of orphans
    * **p_object_name** - the story body variable name
    * **template_object_name** - the story variable name
    * **template_name** - the name of the template
    * **extra_context** - dictionary containing any extra context
    """
    import datetime
    import time

    try:
        pub_date = datetime.date(*time.strptime(year + month + day, '%Y%b%d')[:3])
    except ValueError:
        raise Http404

    qs = Content.published.get
    if request.user.is_staff:
        qs = Content.objects.get

    try:
        content = qs(publish_date=pub_date, slug=slug)
    except Content.DoesNotExist:
        if not settings.THROW_404:
            return render_to_response('content/content_removed.html',
                                      {},
                                      context_instance=RequestContext(request))
        else:
            raise Http404

    template_name = "content/content_detail.html"
    context = {
        template_object_name: content
    }
    if extra_context:
        context.update(extra_context)

    return render_to_response(template_name, context,
                              context_instance=RequestContext(request))

