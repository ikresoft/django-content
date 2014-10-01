from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaks, escape, capfirst
from django.utils.translation import ugettext_lazy as _

from models import Content


ITEMS_PER_FEED = getattr(settings, 'CONTENT_ITEMS_PER_FEED', 50)

class ContentFeed(Feed):

    def __init__(self, *args, **kwargs):
        super(ContentFeed, self).__init__(*args, **kwargs)
        self.site = Site.objects.get_current()

    def title(self):
        return u"%s latest contents" % (self.site.name, )

    def link(self):
        return reverse("content_rss_feed")

    def items(self):
        return Content.objects.order_by('-date_modified')

    def item_title(self, content):
        return content.title

    def item_description(self, content):
        return content.content

    def item_id(self, content):
        return content.guid

    def item_updated(self, content):
        return content.date_modified

    def item_published(self, content):
        return content.date_created

    def item_content(self, content):
        return {"type" : "html", }, linebreaks(escape(content.body))

    def item_links(self, content):
        return [{"href" : reverse("content_detail", args=(content.pk, content.get_slug()))}]

    def item_authors(self, content):
        return [{"name" : content.author}]


class AuthorFeed(ContentFeed):

    def get_object(self, request, author_id):
        return get_object_or_404(Author, pk=author_id)

    def title(self, author):
        return _("Posts by %(author_name)s - %(site_name)s") %\
            {'author_name': author.name, 'site_name': self.site.name}

    def links(self, author):
        return ({'href': reverse("planet_author_show", args=(author.pk, author.get_slug()))},)

    def items(self, author):
        return Content.objects.filter(authors=author,
            ).distinct().order_by("-date_created")[:ITEMS_PER_FEED]


class TagFeed(ContentFeed):

    def get_object(self, request, tag):
        return get_object_or_404(Tag, name=tag)

    def title(self, tag):
        return _("Contents under %(tag)s tag - %(site_name)s") %\
            {'tag': tag, 'site_name': self.site.name}

    def links(self, tag):
        return ({'href': reverse("planet_tag_detail", kwargs={"tag": tag.name})},)

    def items(self, tag):

        return TaggedItem.objects.get_by_model(
            Content.objects.filter(feed__site=self.site), tag)\
            .distinct().order_by("-date_created")[:ITEMS_PER_FEED]


class AuthorTagFeed(ContentFeed):

    def get_object(self, request, author_id, tag):
        self.tag = tag
        return get_object_or_404(Author, pk=author_id)

    def title(self, author):
        return _("Contents by %(author_name)s under %(tag)s tag - %(site_name)s")\
            % {'author_name': author.name, 'tag': self.tag, 'site_name': self.site.name}

    def links(self, author):
        return ({'href': reverse("planet_by_tag_author_show", args=(author.pk, self.tag))},)

    def items(self, author):
        return TaggedItem.objects.get_by_model(
            Content.objects.filter(feed__site=self.site, authors=author), self.tag)\
            .distinct().order_by("-date_created")[:ITEMS_PER_FEED]
