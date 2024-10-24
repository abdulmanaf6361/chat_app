import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message, User
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Handle text messages
        if 'message' in text_data_json:
            message = text_data_json['message']
            receiver_id = text_data_json['receiver_id']
            sender_username = self.scope['user'].username
            timestamp = timezone.now()

            # Find the receiver and chat
            receiver = await self.get_user(receiver_id)
            chat = await self.get_chat(self.scope['user'], receiver, as_seller=self.scope['user'].is_seller)

            # Save the text message to the database
            sender = await self.get_user_by_username(sender_username)
            await self.create_message(chat, sender, message, message_type='text')

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender_username,
                    'timestamp': str(timestamp)
                }
            )

        # Handle file messages (file_url, filename)
        elif 'file_url' in text_data_json:
            file_url = text_data_json['file_url']
            filename = text_data_json['filename']
            sender_username = self.scope['user'].username

            # Find the receiver and chat
            receiver = await self.get_user(text_data_json['receiver_id'])
            chat = await self.get_chat(self.scope['user'], receiver, as_seller=self.scope['user'].is_seller)

            # Save the file message to the database (file metadata)
            sender = await self.get_user_by_username(sender_username)
            await self.create_message(chat, sender, filename, file_url=file_url, message_type='file')

            # Send file metadata to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'file_message',
                    'file_url': file_url,
                    'filename': filename,
                    'sender': sender_username
                }
            )

        elif 'typing' in text_data_json:
            typing = text_data_json['typing']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_notification',
                    'username': self.scope['user'].username,
                    'is_typing': typing
                }
            )


    # Handle text message broadcast
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        }))

    # Handle file metadata broadcast
    async def file_message(self, event):
        file_url = event['file_url']
        filename = event['filename']
        sender = event['sender']

        # Send the file metadata to WebSocket
        await self.send(text_data=json.dumps({
            'file_url': file_url,
            'filename': filename,
            'sender': sender
        }))

    # Handle typing notification
    async def typing_notification(self, event):
        username = event['username']
        is_typing = event['is_typing']

        # Broadcast typing notification to WebSocket
        if username != self.scope['user'].username:
            await self.send(text_data=json.dumps({
                'typing': {
                    'username': username,
                    'is_typing': is_typing
                }
            }))

    # Async method to get the user by ID
    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(pk=user_id)

    # Async method to get the chat based on the user type
    @database_sync_to_async
    def get_chat(self, sender, receiver, as_seller):
        if as_seller:
            return Chat.objects.get(seller=sender, customer=receiver)
        else:
            return Chat.objects.get(seller=receiver, customer=sender)

    # Async method to get the user by username
    @database_sync_to_async
    def get_user_by_username(self, username):
        return User.objects.get(username=username)

    # Async method to create a message
    @database_sync_to_async
    def create_message(self, chat, sender, text=None, file_url=None, message_type='text'):
        if message_type == 'text':
            return Message.objects.create(chat=chat, sender=sender, text=text, message_type='text')
        elif message_type == 'file':
            return Message.objects.create(chat=chat, sender=sender, file=file_url, message_type='file')
