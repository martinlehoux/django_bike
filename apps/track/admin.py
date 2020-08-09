from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from celery import chain

from .models import Track, TrackStat
from . import tasks

User = get_user_model()


class TrackStatInline(admin.StackedInline):
    model = TrackStat


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    inlines = [TrackStatInline]
    fields = (
        "uuid",
        "name",
        "datetime",
        "parser",
        "source_file",
        "points_count",
        "user",
        "public",
        "state",
    )
    readonly_fields = ("uuid", "points_count", "user")
    list_display = ("name", "uuid", "datetime", "points_count", "user", "public")
    actions = ["compute_stats"]

    def save_form(self, request, form, change):
        try:
            form.instance.user
        except User.DoesNotExist:
            form.instance.user = request.user
        return super().save_form(request, form, change)

    def compute_stats(self, request, queryset):
        for track in queryset:
            chain(
                tasks.track_compute_stat.s(track.pk), tasks.track_state_ready.s(),
            ).delay()
        self.message_user(
            request, f"{queryset.count()} computations scheduled.", messages.SUCCESS
        )
