from django.db.models.signals import post_save
from django.dispatch import receiver

from .comment import Comment
from .like import Like
from .track import Track
from .track_stat import TrackStat


@receiver(post_save, sender=Track)
def track_post_save(sender, instance: Track, created: bool, *args, **kwargs):
    if created:
        instance.parse_source()
    if not TrackStat.objects.filter(track=instance).exists():
        if instance.source_file:
            track_stat = TrackStat(track=instance)
            track_stat.compute()
            track_stat.save()
