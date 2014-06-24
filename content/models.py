#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module provides the Content model for reporting news, events, info etc.
"""
import re

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.conf import settings as site_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import select_template
from django.template import Context
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.text import slugify
from django.utils.timezone import now
from polymorphic import PolymorphicModel
from content import settings

from managers import *

from taggit.managers import TaggableManager

class Content(PolymorphicModel):
    """
    A newspaper or magazine type story or document that was possibly also
    printed in a periodical.
    """
    title = models.CharField(_("Title"), max_length=100)
    body = models.TextField(_("Body"), null=True, blank=True)
    slug = models.SlugField(_('Slug'), max_length=100)

    authors = models.ManyToManyField(
        settings.AUTHOR_MODEL,
        verbose_name=_('Authors'),
        blank=True,
        null=True,
        limit_choices_to=settings.AUTHOR_MODEL_LIMIT_CHOICES)

    non_staff_author = models.CharField(
        _('Non-staff author(s)'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_("An HTML-formatted rendering of an author(s) not on staff."))

    date_modified = models.DateTimeField(_("Date modified"), null=True, blank=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    password = models.CharField(max_length=20, null=True, blank=True)
    private = models.BooleanField(default=False)

    allow_comments = models.BooleanField(_('Allow comments'), default=True)

    status = models.IntegerField(_('Published Status'), choices=settings.STATUS_CHOICES, default=settings.DEFAULT_STATUS)

    origin = models.IntegerField(_("Origin"), choices=settings.ORIGIN_CHOICES, default=settings.DEFAULT_ORIGIN,)
    site = models.ManyToManyField(Site, verbose_name=_('Sites'))

    objects = AlternateManager()
    published = CurrentSitePublishedManager()
    if 'taggit' in site_settings.INSTALLED_APPS:
        tags = TaggableManager(blank=True)
    with_counter = PopularContentManager()

    class Meta:
        verbose_name = _("content")
        verbose_name_plural = _("Contents")
        ordering = settings.ORDERING
        get_latest_by = 'date_modified'
        unique_together = ('date_modified', 'slug')

    def get_absolute_url(self):
        pass

    def get_image(self):
        from BeautifulSoup import BeautifulSoup
        from filer.models.imagemodels import Image
        soup = BeautifulSoup(self.body)
        img_tag = soup.find("img", { "front_image" : "true" })
        try:
            id = int(img_tag["filer_id"])
            return Image.objects.get(pk=id)
        except:
            return None
    image = property(get_image)

    def save(self, *args, **kwargs):
        """
        Enforce setting of publish date and time if it is published.
        """
        if self.date_modified is None:
            self.date_modified = now()
        self.slug = self.get_slug()
        super(Content, self).save(*args, **kwargs)

    @property
    def comments_frozen(self):
        """
        Simplified way to get the comment status == frozen
        """
        return self.comment_status == settings.COMMENTS_FROZEN

    @property
    def author(self):
        """
        Easy way to get a combination of authors without having to worry which
        fields are set (author/one-off author)
        """
        import warnings
        warnings.warn('Story.author property is being deprecated, use '
                      '`Story.author_display` instead', DeprecationWarning)

        AuthorModel = models.get_model(*settings.AUTHOR_MODEL.split("."))
        link = '<a href="%s">%s %s</a>'
        if AuthorModel.__module__ == 'django.contrib.auth.models':
            authors = [link % (
                i.get_profile().get_absolute_url(),
                i.first_name,
                i.last_name) for i in self.authors.all()]
        else:
            authors = [link % (i.get_absolute_url(), i.first_name, i.last_name)
                       for i in self.authors.all()]
        if self.non_staff_author:
            authors.append(self.non_staff_author)
        if len(authors) > 1:
            author_string = "%s and %s" % (", ".join(authors[:-1]), authors[-1])
        elif len(authors) == 1:
            author_string = authors[0]
        else:
            author_string = ''
        return mark_safe(author_string)

    @property
    def author_display(self):
        """
        Presentation of the story author(s). Renders the template
        `content/author_display.html` suppling it with the following context

        * **instance** - the story instance
        * **authors** - all the authors (`authors.objects.all()`)
        * **non_staff_author** - text value that can be used in place of `authors`
        """
        template = "content/author_display.html"
        ctx = Context()
        ctx.update({
            'instance': self,
            'authors': self.authors.all(),
            'non_staff_author': self.non_staff_author
        })
        t = select_template([template])
        return t.render(ctx)

    @property
    def paragraphs(self):
        """
        Return the `story.body` as paragraphs by finding all `<p>` tags
        """
        return re.findall("(<p>.+?</p>)", self.body, re.I | re.S)

    if 'content.relations' in site_settings.INSTALLED_APPS:
        def get_related_content_type(self, content_type):
            """
            Get all related items of the specified content type
            """
            return self.storyrelation_set.filter(
                content_type__name=content_type)

        def get_relation_type(self, relation_type):
            """
            Get all relations of the specified relation type
            """
            return self.storyrelation_set.filter(relation_type=relation_type)

    def __unicode__(self):
        return "%s : %s" % (self.title, self.date_modified)


# Reversion integration
if settings.USE_REVERSION:
    rev_error_msg = 'Contents excepts django-reversion to be '\
                    'installed and in INSTALLED_APPS'
    try:
        import reversion
        if not 'reversion' in site_settings.INSTALLED_APPS:
            raise ImproperlyConfigured(rev_error_msg)
    except (ImportError, ):
        raise ImproperlyConfigured(rev_error_msg)

    reversion.register(Content)
