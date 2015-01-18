from django.template import Context, Template, Library
from django.template.defaultfilters import stringfilter


register = Library()


@register.filter
@stringfilter
def render(value):
    return Template(value).render(Context())
