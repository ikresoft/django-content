from django import template
from django.template import RequestContext
from django.template.loader import render_to_string
from categories.views import get_category_for_path
from content.models import Content

register = template.Library()

class ContentByCategoryNode(template.Node):

    def __init__(self, category, limit, var_name, random=False):
        self.var_name = var_name
        self.category = category
        self.limit = limit
        self.random = random
        self.model = Content

    def render(self, context):
        if self.category is None:
            context[self.var_name] = None
            return ''
        try:
            query = Content.published.filter(categories=self.category)
            if self.limit == -1:
                context[self.var_name] = query.all()
            else:
                context[self.var_name] = query.all()[:self.limit]
            if self.limit == 1:
                context[self.var_name] = context[self.var_name][0]
        except:
            context[self.var_name] = None
        return ''

def get_content_by_category(parser, token):
    try:
        tag_name, category, limit, random, _as, var_name = token.split_contents()
    except:
        raise TemplateSyntaxError, "get_content_by_category tag takes exactly four arguments"
    if (category[0] == category[-1] and category[0] in ('"', "'")):
        try:
            category = get_category_for_path(category[1:-1])
        except:
            category = None
    else:
        category = template.Variable(category)
    return ContentByCategoryNode(category, limit, var_name, random)

register.tag('get_content_by_category', get_content_by_category)
