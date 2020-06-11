from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from plotly.offline import plot
from plotly.graph_objs import Scatter, Layout, Figure

from .models import Track, TrackData, smoother
from .forms import TrackCreateForm


class TrackListView(generic.ListView):
    model = Track


class TrackCreateView(LoginRequiredMixin, generic.CreateView):
    model = Track
    template_name_suffix = "_create_form"
    form_class = TrackCreateForm
    success_url = reverse_lazy("track-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TrackDetailView(generic.DetailView):
    model = Track

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        track = self.get_object()
        track_data = TrackData(track)
        alt_vs_dist_fig = Figure(
            data=[
                Scatter(
                    x=track_data.dist(),
                    y=track_data.alt(),
                    mode="lines",
                    name="Altitude",
                ),
                Scatter(
                    x=track_data.dist(),
                    y=track_data.alt_cum(),
                    mode="lines",
                    name="Cumulated altitude",
                ),
            ],
            layout=Layout(
                title=track.name,
                xaxis=dict(title="Distance (km)"),
                yaxis=dict(title="Altitude (m)"),
                margin=dict(r=0, l=0, t=0, b=0),
            ),
        )
        slope_vs_dist_fig = Figure(
            data=[
                Scatter(
                    x=track_data.dist(),
                    y=smoother(track_data.slope()),
                    mode="lines",
                    name="Slope",
                )
            ],
            layout=Layout(
                title=track.name,
                xaxis=dict(title="Distance (km)"),
                yaxis=dict(title="Slope (%)"),
                margin=dict(r=0, l=0, t=0, b=0),
            ),
        )
        speed_vs_dist_fig = Figure(
            data=[
                Scatter(
                    x=track_data.dist(),
                    y=smoother(track_data.speed()),
                    mode="lines",
                    name="Speed",
                )
            ],
            layout=Layout(
                title=track.name,
                xaxis=dict(title="Distance (km)"),
                yaxis=dict(title="Speed (km/h)"),
                margin=dict(r=0, l=0, t=0, b=0),
            ),
        )
        context.update(
            {
                "alt_vs_dist": plot(
                    alt_vs_dist_fig, output_type="div", include_plotlyjs=False
                ),
                "slope_vs_dist": plot(
                    slope_vs_dist_fig, output_type="div", include_plotlyjs=False
                ),
                "speed_vs_dist": plot(
                    speed_vs_dist_fig, output_type="div", include_plotlyjs=False
                ),
            }
        )
        return context
