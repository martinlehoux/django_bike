from django.conf import settings


def settings_context_processor(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
    }
