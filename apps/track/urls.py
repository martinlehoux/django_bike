from django.urls import path

from . import views


app_name = "track"
urlpatterns = [
    path("", views.TrackListView.as_view(), name="list"),
    path("create", views.TrackCreateView.as_view(), name="create"),
    path("<int:pk>", views.TrackDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.TrackDeleteView.as_view(), name="delete"),
]
