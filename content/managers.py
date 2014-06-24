from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.conf import settings as site_settings
from polymorphic.manager import PolymorphicManager
from content import settings

from django.utils import timezone

class CurrentSiteManager(PolymorphicManager):
    "Use this to limit objects to those associated with the current site."
    def __init__(self, field_name=None):
        super(CurrentSiteManager, self).__init__()
        self.__field_name = field_name
        self.__is_validated = False

    def _validate_field_name(self):
        field_names = self.model._meta.get_all_field_names()

        # If a custom name is provided, make sure the field exists on the model
        if self.__field_name is not None and self.__field_name not in field_names:
            raise ValueError("%s couldn't find a field named %s in %s." %
                (self.__class__.__name__, self.__field_name, self.model._meta.object_name))

        # Otherwise, see if there is a field called either 'site' or 'sites'
        else:
            for potential_name in ['site', 'sites']:
                if potential_name in field_names:
                    self.__field_name = potential_name
                    self.__is_validated = True
                    break

        # Now do a type check on the field (FK or M2M only)
        try:
            field = self.model._meta.get_field(self.__field_name)
            if not isinstance(field, (models.ForeignKey, models.ManyToManyField)):
                raise TypeError("%s must be a ForeignKey or ManyToManyField." % self.__field_name)
        except FieldDoesNotExist:
            raise ValueError("%s couldn't find a field named %s in %s." %
                    (self.__class__.__name__, self.__field_name, self.model._meta.object_name))
        self.__is_validated = True

    def get_queryset(self):
        if not self.__is_validated:
            self._validate_field_name()
        return super(CurrentSiteManager, self).get_queryset().filter(**{self.__field_name + '__id__exact': site_settings.SITE_ID})

class CurrentSitePublishedManager(CurrentSiteManager):
    def get_query_set(self):
        queryset = super(CurrentSitePublishedManager, self).get_query_set()
        return queryset.filter(
            date_modified__lte=timezone.now()
        ).filter(
            status__exact=settings.PUBLISHED_STATUS
        )


class AlternateManager(CurrentSiteManager):
    """
    This is the default manager. In some cases, if you only have access to the
    default manager, you can use the published() method to get the right stuff
    """
    def unique_slug(self, date_modified, slug, exclude_id=None):
        """
        Check if the date/slug combination is unique
        """
        query_params = {
            'slug': slug[:100],
            'date_modified__year': date_modified.year,
            'date_modified__month': date_modified.month,
            'date_modified__day': date_modified.day
        }

        qset = self.get_query_set().filter(**query_params)
        if exclude_id:
            qset = qset.exclude(id=exclude_id)
        return qset.count() == 0

    def get_unique_slug(self, date_modified, slug, story_id=None):
        """
        Return a unique slug by adding a digit to the end
        """
        query_params = {
            'date_modified__year': date_modified.year,
            'date_modified__month': date_modified.month,
            'date_modified__day': date_modified.day
        }
        if not self.unique_slug(date_modified, slug, story_id):
            # Allow up to 10,000 versions on the same date
            query_params['slug__startswith'] = slug[:96]
            num = self.get_query_set().filter(**query_params).count()
            slug = '%s%s' % (slug[:96], str(num + 1))
        return slug

    def published(self):
        queryset = self.get_query_set()
        return queryset.filter(
            date_modified__lte=timezone.now()
        ).filter(
            status__exact=settings.PUBLISHED_STATUS)

class PopularContentManager(CurrentSiteManager):

    def get_query_set(self):
        qs = super(PopularContentManager, self).get_query_set()
        content_type = ContentType.objects.get_for_model(self.model).pk
        return qs.extra(select={"counter": "SELECT hits from hitcount_hit_count where content_type_id = %s and object_pk = id" % content_type}).order_by('-counter')
