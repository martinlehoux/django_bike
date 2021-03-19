from django.contrib.auth.models import User
from django.db import models


class Like(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "track"], name="like_unique")
        ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey("track.Track", on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Like: {self.user} @ {self.track} @ {self.datetime}"
