from django.shortcuts import redirect
from django.views.generic import DetailView
from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
)
from django.contrib import messages

User = get_user_model()


class ProfileView(LoginRequiredMixin, DetailView):
    model = User

    def get_object(self, queryset=None):
        return get_user(self.request)


class PasswordChangeDoneView(PasswordChangeDoneView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Your password was changed successfully.")
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
