import re
from django.template.defaultfilters import stringfilter
from django import template
from ..models import NlpExtract, FormAnswer

register = template.Library()


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


@register.filter()
@stringfilter
def bullet_points(string):
    string = string.replace("\no ", "\n• ")
    string = string.replace("\n. \n", "\n")
    string = string.replace("\n. ", "\n• ")
    string = string.replace("\n&#61607; ", "\n• ")
    string = string.replace(" &#9632; \n", "\n• ")
    string = string.replace("\n&#9632; \n", "\n• ")
    string = string.replace("\n&#9632; ", "\n• ")
    string = string.replace(", \n", ", ")
    return string


@register.filter()
@stringfilter
def display_first_line(string):
    string_list = string.split('\n')
    return string_list[0]


@register.filter()
@stringfilter
def double_line_breaks(string):
    return string.replace(".\n", ".\n\n")


@register.filter()
@stringfilter
def strip_all_asterix(string):
    return string.replace("*", "")


@register.filter()
@stringfilter
def next_extract_index(extract_id):
    return None
