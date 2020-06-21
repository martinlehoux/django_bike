from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import Track, TrackStat
from .forms import TrackCreateForm
from . import charts


class TrackListView(generic.ListView):
    model = Track

    def get_queryset(self):
        q = Q(public=True)
        if self.request.user.is_authenticated:
            q |= Q(user=self.request.user)
        return Track.objects.filter(q)


class TrackCreateView(LoginRequiredMixin, generic.CreateView):
    model = Track
    template_name_suffix = "_create_form"
    form_class = TrackCreateForm
    success_url = reverse_lazy("track-list")

    def form_valid(self, form):
        messages.info(
            self.request,
            f"{form.instance.name} track was created and will be parsed in a few seconds",
        )
        form.instance.user = self.request.user
        return super().form_valid(form)


class TrackDetailView(generic.DetailView):
    model = Track

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        track = self.get_object()
        context.update(
            {
                "track_stat": TrackStat(track),
                "charts": [
                    charts.AltVSDistChart(track).plot(),
                    charts.SlopeVSDistChart(track).plot(),
                    charts.SpeedVSDistChart(track).plot(),
                ],
            }
        )
        return context
