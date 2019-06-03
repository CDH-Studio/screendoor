from django import template

register = template.Library()
from django.template.defaultfilters import stringfilter

@register.filter()
@stringfilter
def interpolate(value, arg):
    """
    Interpolates value with argument
    """

    try:
        return format(value % arg)
    except:
        return ''
