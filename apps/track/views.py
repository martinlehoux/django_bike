from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from plotly.offline import plot
from plotly.graph_objs import Scatter, Layout, Figure

from .models import Track
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
        alt_vs_dist_fig = Figure(
            data=[
                Scatter(
                    x=list(track.point_set.values_list("dist", flat=True)),
                    y=list(track.point_set.values_list("alt", flat=True)),
                    mode="lines",
                    name=track.name,
                )
            ],
            layout=Layout(
                title=track.name,
                xaxis=dict(title="Distance (meters)"),
                yaxis=dict(title="Altitude (meters)"),
                margin=dict(r=0, l=0, t=0, b=0),
            ),
        )
        alt_vs_dist = plot(alt_vs_dist_fig, output_type="div", include_plotlyjs=False,)
        context.update({"alt_vs_dist": alt_vs_dist})
        return context
