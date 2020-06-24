from django import template
from django.template.defaultfilters import stringfilter

from ..models import Track

register = template.Library()


@register.filter
@stringfilter
def state_class(value):
    if value == Track.StateChoices.PROCESSING:
        return "is-warning"
    if value == Track.StateChoices.READY:
        return "is-success"
    if value == Track.StateChoices.ERROR:
        return "is-danger"
    return ""
