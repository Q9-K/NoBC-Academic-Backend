from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.room_name = None

    async def connect(self):
        user_email = self.scope['url_route']['kwargs']['user_email']
        self.user = user_email
        self.room_name = f'user_{user_email}'

        # 加入房间分组,一个用户一个组
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 离开房间分组
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    # 接收消息并转发到分组
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 发送消息到分组
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # 从分组接收消息
    async def send_message(self, event):
        message = event['message']
        # 发送消息到 WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
