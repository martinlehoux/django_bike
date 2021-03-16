import rules
from django.contrib.auth.models import User

from .models import Track


@rules.predicate
def is_track_owner(user: User, track: Track) -> bool:
    return track.user == user


@rules.predicate
def track_public(user: User, track: Track) -> bool:
    return track.public


rules.add_perm("track.view_track", is_track_owner | track_public)
rules.add_perm("track.edit_track", is_track_owner)
rules.add_perm("track.delete_track", is_track_owner)
# TODO Add rule for friends
rules.add_perm("track.comment_track", is_track_owner | track_public)
rules.add_perm("track.like_track", track_public)
