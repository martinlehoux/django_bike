from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmdin
from django.contrib.auth.models import User

from apps.account.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profile"


class UserAdmin(BaseUserAdmdin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
