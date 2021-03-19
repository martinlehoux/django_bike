from typing import Any, Dict, List

from django import forms

from apps.main.widgets import TextListInput

from .models import Comment, Track


class TrackCreateForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ["name", "source_file"]

    name = forms.CharField(
        max_length=128, required=True, strip=True, widget=TextListInput
    )
    source_file = forms.FileField(required=True)

    def __init__(self, track_names: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"data_list": track_names})

    def save(self, commit=True):
        self.instance.state = Track.StateChoices.READY
        track = super().save(commit=commit)
        return track


class TrackEditForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ["name", "public", "datetime"]

    name = forms.CharField(
        max_length=128, required=True, strip=True, widget=TextListInput
    )
    # date = forms.DateField(localize=True)
    # time = forms.TimeField(localize=True)

    def __init__(self, track_names: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"data_list": track_names})

    def get_initial_for_field(self, field: forms.Field, field_name: str):
        # if field_name == "date":
        #     return self.instance.datetime.date()
        # if field_name == "time":
        #     return self.instance.datetime.time()
        return super().get_initial_for_field(field, field_name)

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        # cleaned_data["datetime"] = datetime.combine(
        #     cleaned_data["date"], cleaned_data["time"]
        # )
        return cleaned_data


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "cols": 15, "maxlength": 200}),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["text"].label = ""
