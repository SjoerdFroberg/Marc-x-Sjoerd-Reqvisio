from django import template
import os 

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")

@register.filter
def filename(value):
    return os.path.basename(value)


@register.filter
def dict_get(dictionary, key):
    """Custom filter to get a value from a dictionary."""
    return dictionary.get(key, None)



@register.filter
def get_response(responses, args):
    """
    Custom filter to get a specific response based on supplier_id, sku_id, and question_id.
    Args should be formatted as 'supplier_id:sku_id:question_id'.
    """
    supplier_id, sku_id, question_id = map(int, args.split(':'))
    for response in responses:
        if (
            response.supplier_id == supplier_id and
            response.sku_id == sku_id and
            response.question_id == question_id
        ):
            return response
    return None