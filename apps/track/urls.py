from django.urls import path

from . import views

urlpatterns = [
    path("", views.TrackListView.as_view(), name="track-list"),
    path("create", views.TrackCreateView.as_view(), name="track-create"),
    path("<int:pk>", views.TrackDetailView.as_view(), name="track-detail"),
]
