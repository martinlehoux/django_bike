from django import forms

from .models import Track
from . import tasks


class TrackCreateForm(forms.ModelForm):
    source_file = forms.FileField(required=True)

    class Meta:
        model = Track
        fields = ["name", "source_file", "parser"]

    def save(self, commit=True):
        track = super().save(commit=commit)
        (
            tasks.track_parse_source.s(track.pk, self.cleaned_data["parser"])
            | tasks.track_compute_coordinates.s()
            | tasks.track_retrieve_alt.s()
            | tasks.track_compute_dist.s()
        )()
        return track
