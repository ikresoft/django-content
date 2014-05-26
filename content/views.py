#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import EmptyPage, InvalidPage
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.views.generic import ListView, DetailView

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

class ContentViewMixin(object):
    def _get_templates(self):
        return []

    def get_template_names(self, name):
        opts = self.object.get_real_instance()._meta
        app_label = opts.app_label
        search_templates = self._get_templates() + [
            "%s/%ss/%s.html" % (app_label, opts.object_name.lower(), name),
            "%s/%s.html" % (app_label, name),
            "%s.html" % name
        ]

        for template in search_templates:
            try:
                find_template(template)
                return [template]
            except TemplateDoesNotExist:
                pass
        else:  # pragma: no cover
            pass

class ContentListView(ListView, ContentViewMixin):
    model = Content

    def get_queryset(self):
        return self.model.published.all().order_by('-date_modified')

    def get_template_names(self):
        return self.get_template_names('list')


class ContentDetailView(DetailView):
    model = Content

    def get_context_data(self, **kwargs):
        context = super(ContentDetailView, self).get_context_data(**kwargs)

        related_posts = self.model.published.filter(
            tags__name__in=list(self.object.tags.values_list('name', flat=True))
        ).exclude(id=self.object.id).distinct().order_by("-date_modified")
        context['related_posts'] = related_posts[:5]
        return context

    def get_template_names(self):
        return self.get_template_names('detail')
