from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def state_class(value):
    if value == "processing":
        return "is-warning"
    if value == "ready":
        return "is-success"
    return ""
