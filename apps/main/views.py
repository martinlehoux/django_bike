import os
from pathlib import Path

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


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: dict):
        MAX_RELEASES = int(self.request.GET.get("limit", 5))
        context = super().get_context_data(**kwargs)
        files = os.listdir("release-notes")
        tags = list(reversed(sorted(map(get_release_tag, files))))
        if MAX_RELEASES > 0:
            tags = tags[:MAX_RELEASES]
        releases = []
        for file in tags:
            with open(Path("release-notes") / (file + ".yml"), "r") as data:
                release = yaml.safe_load(data)
                release["name"] = get_release_name(file)
                releases.append(release)
        context["releases"] = releases
        return context
