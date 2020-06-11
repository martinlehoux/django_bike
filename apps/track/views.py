from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Track


class TrackListView(generic.ListView):
    model = Track


class TrackCreateView(LoginRequiredMixin, generic.CreateView):
    model = Track
    template_name_suffix = "_create_form"
    fields = ["name", "gpx_file"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TrackDetailView(generic.DetailView):
    model = Track
