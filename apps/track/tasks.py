import celery
from celery.utils.log import get_task_logger

from apps.notification import notify

from .models import Track, TrackStat

logger = get_task_logger(__name__)


def track_error(track: Track, message: str, err: Exception):
    logger.error(message)
    track.state = Track.StateChoices.ERROR
    track.save()
    notify.error(
        track.user,
        f"An error has occured while processing {track} track: {err}",
    )
    raise err


@celery.shared_task
def track_compute_stat(track_pk: int):
    track = Track.objects.get(pk=track_pk)
    try:
        track.trackstat
    except TrackStat.DoesNotExist:
        track.trackstat = TrackStat(track=track)
    track.trackstat.compute()
    track.trackstat.save()
    return track_pk


@celery.shared_task
def track_state_ready(track_pk: int) -> int:
    track = Track.objects.get(pk=track_pk)
    track.state = Track.StateChoices.READY
    track.save()
    notify.success(track.user, f"{track.name} track is ready")
    return track_pk
