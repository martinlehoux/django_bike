from django.contrib import admin

from .models import Track, TrackStat


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

    def save_form(self, request, form, change):
        form.instance.user = request.user
        return super().save_form(request, form, change)
