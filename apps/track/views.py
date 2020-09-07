from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.views import generic
from django.views.generic import edit
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from apps.main.views import PermissionRequiredMethodMixin
from apps.notification import notify
from .models import Track, TrackData
from .forms import TrackCreateForm, TrackEditForm, CommentCreateForm
from . import charts


class TrackListView(generic.ListView):
    model = Track
    paginate_by = 10

    def get_queryset(self):
        q = Q(public=True)
        if self.request.user.is_authenticated:
            q |= Q(user=self.request.user)
        return (
            Track.objects.filter(q)
            .order_by("-datetime")
            .select_related("trackstat", "user")
        )


class TrackCreateView(LoginRequiredMixin, generic.CreateView):
    model = Track
    template_name_suffix = "_create_form"
    form_class = TrackCreateForm
    success_url = reverse_lazy("track:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["track_names"] = list(
            Track.objects.filter(user=self.request.user)
            .values_list("name", flat=True)
            .distinct()
        )
        return kwargs

    def form_valid(self, form):
        notify.info(
            self.request.user,
            f"{form.instance.name} track was created and will be parsed in a few seconds",
        )
        form.instance.user = self.request.user
        return super().form_valid(form)


class TrackDetailView(PermissionRequiredMethodMixin, generic.UpdateView):
    model = Track
    template_name_suffix = "_detail"
    form_class = TrackEditForm
    permission_denied_message = (
        "You are not allowed to access this track: {} with this method."
    )
    raise_exception = True
    permission_required_map = {
        "GET": "track.view_track",
        "POST": "track.edit_track",
    }

    def get_permission_denied_message(self):
        if not hasattr(self, "object"):
            self.object = self.get_object()
        return self.permission_denied_message.format(self.object)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user == self.object.user:
            kwargs["track_names"] = list(
                Track.objects.filter(user=self.request.user)
                .values_list("name", flat=True)
                .distinct()
            )
        else:
            kwargs["track_names"] = []
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        track: Track = self.object
        key = make_template_fragment_key("track_charts", [track.pk])
        if settings.TRACK_CHARTS_DISPLAY and cache.get(key) is None:
            data = TrackData(track)
            context["charts"] = [
                charts.MapChart(track, data).plot(),
                charts.AltVSDistChart(track, data).plot(),
                charts.SlopeVSDistChart(track, data).plot(),
                charts.SpeedVSDistChart(track, data).plot(),
                charts.PowerVSTimeChart(track, data).plot(),
            ]
        context["comment_form"] = CommentCreateForm()
        context["comment_set"] = (
            track.comment_set.select_related("author__profile")
            .all()
            .order_by("-datetime")
        )
        return context


class TrackDeleteView(PermissionRequiredMethodMixin, generic.DeleteView):
    model = Track
    success_url = reverse_lazy("track:list")
    permission_required = "track.delete_track"


class TrackCommentView(PermissionRequiredMethodMixin, generic.CreateView):
    form_class = CommentCreateForm
    permission_required = "track.comment_track"

    def get_success_url(self) -> str:
        return reverse("track:detail", args=[self.object.track.pk])

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.track = get_object_or_404(Track, pk=self.kwargs["pk"])
        return super().form_valid(form)
