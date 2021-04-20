from celery import chain
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.db.models.query import QuerySet

from . import tasks
from .models import Comment, Like, Track, TrackStat


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
        "user",
        "public",
        "state",
    )
    readonly_fields = ("uuid", "user")
    list_display = ("name", "uuid", "datetime", "user", "public", "state")
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "name",
        "datetime",
    ]
    actions = ["parse_source", "compute_stats"]

    def save_form(self, request, form, change):
        try:
            form.instance.user
        except User.DoesNotExist:
            form.instance.user = request.user
        return super().save_form(request, form, change)

    def compute_stats(self, request, queryset: QuerySet[Track]):
        for track in queryset:
            chain(
                tasks.track_compute_stat.s(track.pk),
                tasks.track_state_ready.s(),
            ).delay()
        self.message_user(
            request, f"{queryset.count()} computations scheduled.", messages.SUCCESS
        )

    def parse_source(self, request, queryset: QuerySet[Track]):
        for track in queryset:
            chain(
                tasks.track_parse_source.s(track.pk),
                tasks.track_state_ready.s(),
            ).delay()
        self.message_user(
            request, f"{queryset.count()} computations scheduled.", messages.SUCCESS
        )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    fields = ["author", "track", "text", "datetime"]
    readonly_fields = ["author", "track", "datetime"]
    list_display = ["author", "track", "datetime"]
    search_fields = [
        "author__username",
        "author__first_name",
        "author__last_name",
        "track__name",
        "datetime",
    ]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["user", "track", "datetime"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "track__name",
        "datetime",
    ]
    list_display_links = None
