from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.main.views import IndexView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.account.urls")),
    path("", IndexView.as_view(), name="index"),
    path("track/", include("apps.track.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
