from django import template
from django.template.defaultfilters import stringfilter

from ..models import Like, Track

register = template.Library()


@register.filter
@stringfilter
def state_class(value):
    if value == Track.StateChoices.PROCESSING:
        return "is-loading is-warning"
    if value == Track.StateChoices.READY:
        return "is-success"
    if value == Track.StateChoices.ERROR:
        return "is-danger"
    return ""


@register.filter
@stringfilter
def state_icon(value):
    if value == Track.StateChoices.PROCESSING:
        return ""
    if value == Track.StateChoices.READY:
        return "fa-map-marked"
    if value == Track.StateChoices.ERROR:
        return "fa-ban"
    return ""


@register.simple_tag
def user_likes_track(user, track):
    return Like.objects.filter(user=user, track=track).exists()


@register.filter
@stringfilter
def sport_icon(value):
    if value == Track.SportChoices.BIKING:
        return "fa-biking"
    if value == Track.SportChoices.RUNNING:
        return "fa-running"
