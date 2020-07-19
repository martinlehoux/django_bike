from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, FormView
from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordResetView,
)

from apps.notification import notify

from .forms import AvatarForm
from .models import Profile

User = get_user_model()


class ProfileView(LoginRequiredMixin, DetailView):
    model = User

    def get_object(self, queryset=None):
        return get_user(self.request)

    def get_context_data(self, **kwags):
        context = super().get_context_data(**kwags)
        context["avatar_form"] = AvatarForm(instance=self.request.user)
        return context


class AvatarUploadView(LoginRequiredMixin, UpdateView):
    form_class = AvatarForm
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return get_user(self.request).profile


class PasswordChangeDoneView(PasswordChangeDoneView):
    def dispatch(self, request, *args, **kwargs):
        notify.success(
            request.user, "Your password was changed successfully.",
        )
        return redirect("profile")


class PasswordResetDoneView(PasswordResetDoneView):
    def dispatch(self, request, *args, **kwargs):
        messages.info(
            request,
            (
                "We’ve emailed you instructions for setting your password, "
                "if an account exists with the email you entered. You should "
                "receive them shortly. If you don’t receive an email, please "
                "make sure you’ve entered the address you registered with, and "
                "check your spam folder."
            ),
        )
        return redirect("login")


class PasswordResetCompleteView(PasswordResetCompleteView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Password reset complete")
        return redirect("login")


class PasswordResetView(PasswordResetView):
    email_template_name = "email/password_reset/email.txt"
    html_email_template_name = "email/password_reset/email.html"
