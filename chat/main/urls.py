# chat/urls.py
from django.urls import path
from .views import register_view, login_view, logout_view,home_view,chat_room

app_name = 'chat'

urlpatterns = [
    path('', home_view, name='home'),  # Add home URL
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('chat/<str:room_name>/', chat_room, name='room'),
]
