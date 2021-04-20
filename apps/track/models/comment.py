from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.db import models


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey("track.Track", on_delete=models.CASCADE)
    text = models.TextField(blank=False, validators=[MaxLengthValidator(200)])
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment: {self.author} @ {self.track} @ {self.datetime}"
