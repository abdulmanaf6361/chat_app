# chat/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm

from django.shortcuts import render

def home_view(request):
    return render(request, 'chat/home.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat:home')  # Redirect to home after registration
    else:
        form = UserRegisterForm()
    return render(request, 'chat/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chat:home')
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('chat:login')


# chat/views.py
from django.shortcuts import render, get_object_or_404
from .models import Chat, Message
from django.contrib.auth.decorators import login_required

@login_required
def chat_room(request, room_name):
    # Ensure the user is either a seller or customer in this chat room
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'username': request.user.username
    })
