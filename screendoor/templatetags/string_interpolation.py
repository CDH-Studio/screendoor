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


@register.filter()
@stringfilter
def strip(string):
    return string.strip()


@register.filter()
def has_education(list):
    for item in list:
        if item.requirement_type == "Education":
            return True
    return False


@register.filter()
def has_experience(list):
    for item in list:
        if item.requirement_type == "Experience":
            return True
    return False


@register.filter()
def has_assets(list):
    for item in list:
        if item.requirement_type == "Asset":
            return True
    return False
