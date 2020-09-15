from django import template
from django.template.defaultfilters import stringfilter

from ..models import Track, Like

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


@register.simple_tag
def user_likes_track(user, track):
    return Like.objects.filter(user=user, track=track).exists()
