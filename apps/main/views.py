import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, TypedDict

import yaml
from django.views.generic import TemplateView


def get_release_tag(filename: str) -> str:
    *parts, ext = filename.split(".")
    assert ext == "yml"
    return ".".join(parts)


def get_release_name(tag: str) -> str:
    parts = tag.split(".")
    if len(parts) == 2:
        prefix = "Release"
    elif len(parts) == 3:
        prefix = "Patch"
    else:
        prefix = "Unknown"
    return f"{prefix} {'.'.join(parts)}"


def tag_key(tag: str) -> Tuple[int, int, int]:
    parts = [int(p) for p in tag.split(".")]
    if len(parts) == 2:
        parts.append(0)
    return tuple(parts)


def get_all_tags() -> List[str]:
    files = os.listdir("release-notes")
    parsed_tags = map(get_release_tag, files)
    sorted_tags = sorted(parsed_tags, key=tag_key)
    tags = reversed(sorted_tags)
    return list(tags)


class ReleaseNote(TypedDict):
    name: str
    date: datetime
    features: Dict[str, str]
    fixes: Dict[str, str]


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: dict):
        MAX_RELEASES = int(self.request.GET.get("limit", 5))
        context = super().get_context_data(**kwargs)
        tags = get_all_tags()
        if MAX_RELEASES > 0:
            tags = tags[:MAX_RELEASES]
        releases = []
        for file in tags:
            with open(Path("release-notes") / (file + ".yml"), "r") as data:
                release: ReleaseNote = yaml.safe_load(data)
                release["name"] = get_release_name(file)
                releases.append(release)
        context["releases"] = releases
        return context
