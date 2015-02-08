from django import template
from django.template import TemplateSyntaxError
from django.utils import translation
from categories.views import get_category_for_path
from content.models import CategoryContent, Category

register = template.Library()


@register.filter
def content_url(value, category):
    return value.get_absolute_url(category)


@register.simple_tag(takes_context=True)
def get_next_path(context, lang):
    request = context["request"]
    if hasattr(request, 'content_object'):
        translation.activate(lang)
        s = request.content_object.get_absolute_url(None, lang)
        translation.deactivate()
        return s
    return request.get_full_path()


class ContentByCategoriesNode(template.Node):

    def __init__(self, categories, limit, var_name, random=False):
        self.var_name = var_name
        self.categories = categories
        self.limit = int(limit)
        self.random = True if random is True else False
        self.model = CategoryContent

    def render(self, context):
        if self.categories is None or self.categories == []:
            context[self.var_name] = None
            return ''
        try:
            query = self.model.published.all()
            if self.categories is not None and self.categories != []:
                if isinstance(self.categories[0], template.Variable):
                    self.categories = [self.categories[0].resolve(context)]
                query = query.filter(categories__in=self.categories)

            ordering = '-date_modified'
            if self.random is True:
                ordering = '?'
            query = query.order_by(ordering)
            if self.limit == -1:
                context[self.var_name] = query.all()
            else:
                context[self.var_name] = query.all()[:self.limit]
            if self.limit == 1:
                context[self.var_name] = context[self.var_name][0]
        except:
            context[self.var_name] = None
        return ''


def get_content_by_categories(parser, token):
    try:
        tag_name, categories, limit, random, _as, var_name = token.split_contents()
    except:
        raise TemplateSyntaxError("get_content_by_category tag takes exactly four arguments")
    categories_array = []
    if categories != '':
        if (categories[0] == categories[-1] and categories[0] in ('"', "'")):
            try:
                cats = [x.strip() for x in categories[1:-1].split(',')]
                for cat in cats:
                    categories_array.append(get_category_for_path(cat, queryset=Category.objects.all()))
            except:
                pass
        else:
            categories_array.append(template.Variable(categories))
    return ContentByCategoriesNode(categories_array, limit, var_name, random)

register.tag('get_content_by_categories', get_content_by_categories)


class LatestContent(template.Node):

    def __init__(self, limit, category_list, var_name):
        self.var_name = var_name
        self.category_list = category_list
        self.limit = int(limit)
        self.model = CategoryContent

    def render(self, context):

        try:
            query = self.model.published.order_by("-date_modified")
        except:
            query = self.model.published.order_by("-date_created")

        if self.category_list is not None and self.category_list != []:
            if isinstance(self.category_list[0], template.Variable):
                self.category_list = [self.category_list[0].resolve(context)]
            query = query.filter(categories__in=self.category_list)

        if self.limit == -1:
            context[self.var_name] = query.all()
        else:
            context[self.var_name] = query.all()[:self.limit]

        return ''


@register.tag()
def get_latest_content(parser, token):
    try:
        tag_name, limit, category, _as, var_name = token.split_contents()
    except:
        raise TemplateSyntaxError("get_latest_posts tag takes exactly three arguments")

    category_list = []
    if category != '':
        if (category[0] == category[-1] and category[0] in ('"', "'")):
            try:
                cats = [x.strip() for x in category[1:-1].split(',')]
                for cat in cats:
                    category_list.append(get_category_for_path(cat, queryset=Category.objects.all()))
            except:
                pass
        else:
            category_list.append(template.Variable(category))

    return LatestContent(limit, category_list, var_name)


class PopularContent(template.Node):

    def __init__(self, limit, category, var_name):
        self.var_name = var_name
        self.category = category
        self.limit = int(limit)

    def render(self, context):
        from datetime import timedelta, date
        enddate = date.today()
        startdate = enddate - timedelta(days=1)
        query = CategoryContent.with_counter.filter(date_modified__range=[startdate, enddate])
        print query
        if not query:
            startdate = enddate - timedelta(days=2)
            query = CategoryContent.with_counter.filter(date_modified__range=[startdate, enddate])

        if self.category is not None:
            self.category = self.category.resolve(context)
            query = query.filter(categories=self.category)

        if self.limit == -1:
            context[self.var_name] = query.all()
        else:
            context[self.var_name] = query.all()[:self.limit]

        return ''


@register.tag()
def get_popular_content(parser, token):
    try:
        tag_name, limit, category, _as, var_name = token.split_contents()
    except:
        raise TemplateSyntaxError("get_popular_posts tag takes exactly three arguments")

    if category != '':
        if (category[0] == category[-1] and category[0] in ('"', "'")):
            try:
                category = get_category_for_path(category[1:-1], queryset=Category.objects.all())
            except:
                category = None
        else:
            category = template.Variable(category)

    return PopularContent(limit, category, var_name)


@register.filter
def youtube_url(value):
    from urlparse import urlparse, parse_qs
    try:
        return 'http://www.youtube.com/embed/%s?feature=oembed' % parse_qs(urlparse(value).query)["v"][0]
    except:
        return ''
