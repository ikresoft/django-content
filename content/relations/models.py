#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext as _

from content import settings as content_settings
from content.models import Content

CONTENT_RELATION_LIMITS = []
if content_settings.RELATION_MODELS:
    CONTENT_RELATION_LIMITS = reduce(lambda x, y: x|y, content_settings.RELATIONS)


class ContentRelationManager(models.Manager):
    """Basic manager with a few convenience methods"""

    def get_content_type(self, content_type):
        """
        Get all the related items with a specific content_type
        """
        qs = self.get_query_set()
        return qs.filter(content_type__name=content_type)

    def get_relation_type(self, relation_type):
        """
        Get all the related items with a specific relation_type
        """
        qs = self.get_query_set()
        return qs.filter(relation_type=relation_type)


class ContentRelation(models.Model):
    """Related story item"""

    content = models.ForeignKey(Content)
    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=STORY_RELATION_LIMITS)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    relation_type = models.CharField(_("Relation Type"),
        max_length="200",
        blank=True,
        null=True,
        help_text=_(
            _("A generic text field to tag a relation, such as 'leadphoto'.")))

    objects = ContentRelationManager()

    class Meta:
        db_table = 'content_contentrelation'

    def __unicode__(self):
        return unicode(self.content_object)
