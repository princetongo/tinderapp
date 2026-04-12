import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        # Create a consistent room name regardless of who initiates
        ids = sorted([self.user.id, int(self.other_user_id)])
        self.room_name = f"chat_{ids[0]}_{ids[1]}"
        self.room_group_name = f"chat_{ids[0]}_{ids[1]}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Update last seen
        await self.update_last_seen()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            content = data.get('content', '').strip()
            if not content:
                return

            # Check users are matched before saving
            is_matched = await self.check_match()
            if not is_matched:
                return

            message = await self.save_message(content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'content': content,
                    'sender_id': self.user.id,
                    'sender_name': await self.get_sender_name(),
                    'timestamp': message.created_at.strftime('%H:%M'),
                }
            )
        elif message_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': self.user.id,
                    'is_typing': data.get('is_typing', False),
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'content': event['content'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
        }))

    async def typing_indicator(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'is_typing': event['is_typing'],
            }))

    @database_sync_to_async
    def save_message(self, content):
        from .models import Message
        from accounts.models import User
        receiver = User.objects.get(id=self.other_user_id)
        return Message.objects.create(
            sender=self.user,
            receiver=receiver,
            content=content
        )

    @database_sync_to_async
    def check_match(self):
        from matching.models import Match
        from django.db.models import Q
        return Match.objects.filter(
            Q(user1=self.user, user2_id=self.other_user_id) |
            Q(user1_id=self.other_user_id, user2=self.user),
            is_active=True
        ).exists()

    @database_sync_to_async
    def get_sender_name(self):
        try:
            return self.user.profile.first_name
        except Exception:
            return self.user.username

    @database_sync_to_async
    def update_last_seen(self):
        self.user.update_last_seen()
