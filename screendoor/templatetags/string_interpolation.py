import re
from django.template.defaultfilters import stringfilter
from django import template

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
def analysis_linebreaks(string):
    string_list = string.split('\n')
    new_string = []
    for string in string_list:
        if not string == '':
            new_string.append("• " + string[0].upper() +
                          string[1:len(string)] + "\n \n")
    return "".join(new_string)


@register.filter()
@stringfilter
def double_linebreaks(string):
    string_list = string.split('\n')
    new_string = []
    for string in string_list:
        new_string.append("" + string + "\n \n")
    return "".join(new_string)


@register.filter()
@stringfilter
def display_first_line(string):
    string_list = string.split('\n')
    return string_list[0]


@register.filter()
@stringfilter
def fix_double_asterix(string):
    string_list = string.split("**")
    new_string = []
    counter = 0
    for string_in_list in string_list:
        if counter > 1:
            new_string.append("\n \n**"
                              + string_in_list)
        else:
            new_string.append(string_in_list)
        counter += 1
    return "".join(new_string)


@register.filter()
@stringfilter
def fix_single_asterix(string):
    string_list = string.split("*")
    new_string = []
    counter = 0
    for string_in_list in string_list:
        if counter > 2:
            new_string.append("\n \n"
                              + string_in_list)
        else:
            new_string.append(string_in_list)
        counter += 1
    return "".join(new_string)


@register.filter()
@stringfilter
def strip_all_asterix(string):
    return string.replace("*", "")
