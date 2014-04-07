#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module provides the Content model for reporting news, events, info etc.
"""
import re

from datetime import datetime

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
from polymorphic import PolymorphicModel
from content import settings

from categories.fields import CategoryFKField, CategoryM2MField

from managers import *

from taggit.managers import TaggableManager

class Content(PolymorphicModel):
    """
    A newspaper or magazine type story or document that was possibly also
    printed in a periodical.
    """
    title = models.CharField(
        _("Title"),
        max_length=100)
    slug = models.SlugField(
        _('Slug'),
        max_length=50)
    categories = CategoryM2MField(null=True, blank=True)
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
    publish_date = models.DateField(
        _('Publish Date'),
        help_text=_("The date the original story was published"),
        blank=True,
        null=True)
    publish_time = models.TimeField(
        _('Publish Time'),
        help_text=_("The time the original story was published"),
        blank=True,
        null=True)
    update_date = models.DateTimeField(
        _('Update Date'),
        help_text=_("The update date/time to display to the user"),
        blank=True,
        null=True)
    modified_date = models.DateTimeField(
        _("Date Modified"),
        auto_now=True,
        blank=True,
        editable=False)

    print_pub_date = models.DateTimeField(
        _('Print Publish Date'),
        blank=True,
        null=True),
    print_section = models.CharField(
        _('Print Section'),
        max_length=30,
        blank=True,
        null=True),
    print_page = models.CharField(
        _('Print Page'),
        max_length=5,
        blank=True,
        null=True),

    comments = models.BooleanField(
        _('Enable Comments?'),
        default=True)
    comment_status = models.IntegerField(
        _('Comment Status'),
        choices=settings.COMMENT_STATUSES,
        default=1
    )
    status = models.IntegerField(
        _('Published Status'),
        choices=settings.STATUS_CHOICES,
        default=settings.DEFAULT_STATUS)
    body = models.TextField(_("Body"), null=True, blank=True)
    origin = models.IntegerField(
        _("Origin"),
        choices=settings.ORIGIN_CHOICES,
        default=settings.DEFAULT_ORIGIN,)
    site = models.ManyToManyField(Site, verbose_name=_('Sites'))

    objects = AlternateManager()
    published = CurrentSitePublishedManager()
    tags = TaggableManager(blank=True)
    with_counter = PopularPostManager()

    class Meta:
        verbose_name = _("content")
        verbose_name_plural = _("Contents")
        ordering = settings.ORDERING
        get_latest_by = 'publish_date'
        unique_together = ('publish_date', 'slug')

    def get_absolute_url(self):
        pass

    def get_front_image(self):
        from BeautifulSoup import BeautifulSoup
        from filer.models.imagemodels import Image
        soup = BeautifulSoup(self.body)
        img_tag = soup.find("img", { "front_image" : "true" })
        try:
            id = int(img_tag["filer_id"])
            return Image.objects.get(pk=id)
        except:
            return None

    def save(self, *args, **kwargs):
        """
        Enforce setting of publish date and time if it is published.
        """
        if self.status == settings.PUBLISHED_STATUS:
            if not self.publish_date:
                self.publish_date = datetime.now().date()
            if not self.publish_time:
                self.publish_time = datetime.now().time()
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
        return "%s : %s" % (self.title, self.publish_date)


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
