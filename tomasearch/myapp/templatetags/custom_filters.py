from django import template

register = template.Library()

@register.filter
def get_attribute(obj, attr_name):
    return obj.get(attr_name, '')

@register.filter
def scientific_notation(value):
    try:
        return f"{float(value):.6e}"
    except (ValueError, TypeError):
        return value