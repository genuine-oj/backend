from channels.generic.websocket import AsyncJsonWebsocketConsumer


class SubmissionConsumer(AsyncJsonWebsocketConsumer):
    room_name = None
    room_group_name = None

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['submission_id']
        self.room_group_name = 'submission_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        print(content)
