from django.urls import path, include

from . import views


urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("", include("django.contrib.auth.urls")),
]
