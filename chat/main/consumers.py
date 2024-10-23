import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, Message, User
from django.utils import timezone
from django.utils.dateformat import format as date_format

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
        message = text_data_json['message']
        receiver_id = text_data_json['receiver_id']  # Get the receiver's ID from the message data
        sender_username = self.scope['user'].username

        # Get current timestamp
        timestamp = timezone.now()

        # Format timestamp to "Oct. 23, 2024, 12:18 p.m."
        formatted_timestamp = date_format(timestamp, 'M. j, Y, P')

        # Find the receiver by the ID (async operation)
        receiver = await self.get_user(receiver_id)

        # Determine whether the sender is a seller or a customer and find the chat
        if self.scope['user'].is_seller:
            chat = await self.get_chat(self.scope['user'], receiver, as_seller=True)
        else:
            chat = await self.get_chat(self.scope['user'], receiver, as_seller=False)

        # Save the message to the database (async operation)
        sender = await self.get_user_by_username(sender_username)
        await self.create_message(chat, sender, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username,
                'timestamp': formatted_timestamp  # Send the formatted timestamp
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']  # Receive the timestamp from the event

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp  # Include the timestamp in the WebSocket message
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
    def create_message(self, chat, sender, text):
        return Message.objects.create(chat=chat, sender=sender, text=text)
