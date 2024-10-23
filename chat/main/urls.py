# chat/urls.py
from django.urls import path
from .views import register_view, login_view, logout_view,home_view,chat_room,chat_list,create_chat

app_name = 'chat'

urlpatterns = [
    path('', home_view, name='home'),  # Add home URL
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('chat-list/', chat_list, name='chat_list'),  # List of chats
    path('chat/create/', create_chat, name='create_chat'),  # Create a new chat
    path('chat/<str:room_name>/',chat_room, name='chat_room'),  # Chat room
]
