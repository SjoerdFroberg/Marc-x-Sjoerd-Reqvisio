from django import template
import os 

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")

@register.filter
def filename(value):
    return os.path.basename(value)


