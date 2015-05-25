#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template import TemplateDoesNotExist
from django.template.loader import find_template
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.views.generic import ListView, DetailView

from content import settings
from .models import Content, CategoryContent, Category
from categories.views import get_category_for_path


@staff_member_required
def admin_changeset_list(request, content_id, template_name='admin/content/changesets.html'):
    try:
        content = Content.objects.get(pk=content_id)
    except Content.DoesNotExist:
        raise Http404

    chsets = content.changeset_set.all().order_by('-revision')

    return render_to_response(template_name,
                              {'content': content,
                               'changesets': chsets},
                              context_instance=RequestContext(request))


class ContentViewMixin(object):

    def get_extra_data(self, **kwargs):
        return {}

    def _get_templates(self, name):
        return []

    def get_template_names(self, name):
        opts = self.model._meta
        app_label = opts.app_label
        search_templates = self._get_templates(name) + [
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
        else:
            pass


class ContentListView(ContentViewMixin, ListView):
    model = Content

    def get_context_data(self, **kwargs):
        context = super(ContentListView, self).get_context_data(**kwargs)
        context.update(self.get_extra_data(**kwargs))
        return context

    def get_queryset(self):
        return self.model.published.all().order_by('-date_modified')

    def get_template_names(self):
        if self.template_name is not None and self.template_name != '':
            return self.template_name
        return ContentViewMixin.get_template_names(self, 'list')


class ContentDetailView(DetailView, ContentViewMixin):
    model = Content

    def get_context_data(self, **kwargs):
        context = super(ContentDetailView, self).get_context_data(**kwargs)

        related_posts = self.model.published.filter(
            tags__name__in=list(self.object.tags.values_list('name', flat=True))
        ).exclude(id=self.object.id).distinct().order_by("-date_modified")
        context['related_content'] = related_posts[:5]
        context.update(self.get_extra_data(**kwargs))
        return context

    def get_template_names(self):
        if self.template_name is not None and self.template_name != '':
            return self.template_name
        return ContentViewMixin.get_template_names(self, 'detail')


def get_sub_categories(category):
    qs = category.get_descendants()
    categories = [category.pk]
    for node in qs:
        categories.append(node.pk)
    return categories


class CategoryContentViewMixin(ContentViewMixin):

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'category'):
            try:
                self.category = get_category_for_path(self.kwargs["path"], queryset=Category.objects.all())
            except:
                raise Http404
        return super(CategoryContentViewMixin, self).dispatch(request, *args, **kwargs)

    def get_extra_data(self, **kwargs):
        extra_data = {}
        extra_data['category'] = self.category
        return extra_data

    def _get_templates(self, name):
        opts = self.model._meta
        app_label = opts.app_label
        path = CategoryContent.get_path(self.category)
        return ["%s/%ss/%s/%s.html" % (app_label, opts.object_name.lower(), path, name)]


class CategoryContentListView(CategoryContentViewMixin, ContentListView):
    model = CategoryContent

    def get_context_data(self, **kwargs):
        context = super(CategoryContentListView, self).get_context_data(**kwargs)

        paginator = Paginator(self.qs, settings.PAGINATION["P_PER_PAGE"])
        page = self.request.GET.get("page")
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['object_list'] = posts
        return context

    def get_queryset(self):
        qs = super(CategoryContentListView, self).get_queryset()
        self.qs = qs.filter(categories__in=get_sub_categories(self.category))
        return qs


class CategoryContentDetailView(CategoryContentViewMixin, ContentDetailView):
    model = CategoryContent

    def get(self, request, *args, **kwargs):
        request.content_object = self.get_object()
        return super(CategoryContentDetailView, self).get(request, *args, **kwargs)
