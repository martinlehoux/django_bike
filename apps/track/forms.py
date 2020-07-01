from typing import List

from django import forms

from apps.main.widgets import TextListInput
from .models import Track
from . import tasks


class TrackCreateForm(forms.ModelForm):
    name = forms.CharField(
        max_length=128, required=True, strip=True, widget=TextListInput
    )
    source_file = forms.FileField(required=True)

    def __init__(self, track_names: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"data_list": track_names})

    class Meta:
        model = Track
        fields = ["name", "source_file", "parser"]

    def save(self, commit=True):
        self.instance.state = Track.StateChoices.PROCESSING
        track = super().save(commit=commit)
        (
            tasks.track_parse_source.s(track.pk, self.cleaned_data["parser"])
            | tasks.track_compute_coordinates.s()
            | tasks.track_retrieve_alt.s()
            | tasks.track_compute_dist.s()
            | tasks.track_state_ready.s()
        )()
        return track
