from django.http.response import JsonResponse, HttpResponse
from django.http.request import HttpRequest
from django.views.decorators import csrf

from .models import Notification


def get_notifications(request):
    # Notification.objects.create(user=request.user, content="test")
    return JsonResponse(
        [
            {"content": notif.content, "pk": notif.pk, "level": notif.level}
            for notif in Notification.objects.all()
        ],
        safe=False,
    )


@csrf.csrf_exempt
def detail_notif(request: HttpRequest, pk: int):
    if request.method == "DELETE":
        Notification.objects.get(pk=pk).delete()
        return HttpResponse(status=204)
