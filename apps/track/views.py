from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings

from apps.main.views import PermissionRequiredMethodMixin
from .models import Track
from .forms import TrackCreateForm, TrackEditForm
from . import charts


class TrackListView(generic.ListView):
    model = Track

    def get_queryset(self):
        q = Q(public=True)
        if self.request.user.is_authenticated:
            q |= Q(user=self.request.user)
        return Track.objects.filter(q).order_by("-datetime")


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
        messages.info(
            self.request,
            f"{form.instance.name} track was created and will be parsed in a few seconds",
        )
        form.instance.user = self.request.user
        return super().form_valid(form)


class TrackDetailView(PermissionRequiredMethodMixin, generic.UpdateView):
    model = Track
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
        track = self.get_object()
        return self.permission_denied_message.format(track)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["track_names"] = list(
            Track.objects.filter(user=self.request.user)
            .values_list("name", flat=True)
            .distinct()
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        track: Track = self.get_object()
        context["track_stat"] = track.trackstat
        if settings.TRACK_CHARTS_DISPLAY:
            context["charts"] = [
                charts.MapChart(track).plot(),
                charts.AltVSDistChart(track).plot(),
                charts.SlopeVSDistChart(track).plot(),
                charts.SpeedVSDistChart(track).plot(),
                charts.PowerVSTimeChart(track).plot(),
            ]
        return context


class TrackDeleteView(PermissionRequiredMethodMixin, generic.DeleteView):
    model = Track
    success_url = reverse_lazy("track:list")
    permission_required = "track.delete_track"
