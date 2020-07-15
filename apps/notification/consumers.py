from typing import List

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Notification


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        await self.channel_layer.group_add(self.user.username, self.channel_name)
        await self.accept()
        notifications = await self.get_all_notifications(self.user)
        await self.send_json({"type": "list", "notifications": notifications})

    async def disconnect(self, code):
        pass

    async def receive_json(self, data):
        if data["type"] == "delete":
            notification = await self.get_notification(user=self.user, pk=data["pk"])
            await database_sync_to_async(notification.delete)()
            await self.send_json({"type": "delete", "pk": data["pk"]})

    async def new_notification(self, event):
        await self.send_json({"type": "new", "notification": event["notification"]})

    @database_sync_to_async
    def get_all_notifications(self, user) -> List[Notification]:
        return [notif.json for notif in Notification.objects.filter(user=user)]

    @database_sync_to_async
    def get_notification(self, user, pk: int) -> Notification:
        return Notification.objects.get(user=user, pk=pk)
