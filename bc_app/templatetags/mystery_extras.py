from django import template
from bc_app.views import sanitize_name

register = template.Library()


@register.filter(name='split')
def split(value, key):
    return value.split(key)


@register.filter(name='value_subt')
def value_subt(val1, val2):
    return int(val1) - int(val2)


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='get_sanitize_name')
def get_sanitize_name(string_name):
    return sanitize_name(string_name)
