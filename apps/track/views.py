from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

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
