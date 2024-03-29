from logging import getLogger

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notification import notify

from .comment import Comment
from .like import Like
from .track import Track
from .track_stat import TrackStat

logger = getLogger(__name__)


@receiver(post_save, sender=Track)
def track_post_save(sender, instance: Track, created: bool, *args, **kwargs):
    if created:
        try:
            instance.parse_source()
        except Exception as err:
            notify.error(
                instance.user,
                f"An error occurred while parsing the track {instance.uuid}: {err}",
            )
            logger.warning(err)
            instance.state = Track.StateChoices.ERROR
            instance.save()
    if not TrackStat.objects.filter(track=instance).exists():
        if instance.source_file:
            track_stat = TrackStat(track=instance)
            track_stat.compute()
            track_stat.save()
