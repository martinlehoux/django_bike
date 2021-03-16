from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    fields = ["datetime", "user", "level", "content"]
    readonly_fields = ["datetime"]
    list_display = ["datetime", "user", "level"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "datetime",
    ]
