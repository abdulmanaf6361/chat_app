# chat/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required

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

@login_required
def chat_list(request):
    # Fetch all chats where the user is either the seller or the customer
    if request.user.is_seller:
        chats = Chat.objects.filter(seller=request.user)
    else:
        chats = Chat.objects.filter(customer=request.user)

    return render(request, 'chat/chat_list.html', {
        'chats': chats,
    })

from django.http import HttpResponseForbidden

@login_required
def create_chat(request):
    if request.method == 'POST':
        print("called")
        receiver_id = request.POST.get('receiver_id')
        try:
            receiver = User.objects.get(pk=receiver_id)
        except User.DoesNotExist:
            return render(request, 'chat/create_chat.html', {'error': 'User not found'})

        # Ensure the user is not trying to chat with someone of the same type
        if request.user.is_seller and receiver.is_seller:
            return HttpResponseForbidden("Sellers can't chat with other sellers.")
        if request.user.is_customer and receiver.is_customer:
            return HttpResponseForbidden("Customers can't chat with other customers.")

        # Create or get the chat if it already exists
        if request.user.is_seller:
            chat, created = Chat.objects.get_or_create(seller=request.user, customer=receiver)
        else:
            chat, created = Chat.objects.get_or_create(seller=receiver, customer=request.user)

        request.session['receiver_id'] = receiver_id

        # Redirect to the chat room, passing receiver_id as a query parameter
        return redirect('chat:chat_room', room_name=chat.pk)

    return render(request, 'chat/create_chat.html')



# chat/views.py
from django.shortcuts import render, get_object_or_404
from .models import Chat, Message
from django.contrib.auth.decorators import login_required

# chat/views.py
from django.shortcuts import render, get_object_or_404
from .models import Chat, Message
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect
from .models import Chat, Message
from django.contrib.auth.decorators import login_required
from django.http import Http404,HttpResponseBadRequest
from main.models import User

@login_required
def chat_room(request, room_name):
    # Fetch the chat object using the primary key (room_name in this case is the chat ID)
    receiver_id = request.session.get('receiver_id')

    chat = get_object_or_404(Chat, pk=room_name)
    if request.user == chat.seller:
        receiver = chat.customer
    elif request.user == chat.customer:
        receiver = chat.seller
    else:
        return HttpResponseForbidden("You do not have access to this chat.")


    # Fetch past messages for this chat
    messages = Message.objects.filter(chat=chat).order_by('timestamp')

    # Format the timestamps
    for message in messages:
        message.timestamp_formatted = message.timestamp.strftime('%d/%m/%Y, %H:%M:%S')

    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'username': request.user.username,
        'messages': messages,  # Pass messages to the template
        'receiver_id':receiver.id
    })

from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Disable CSRF for simplicity (ensure proper security in production)
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        receiver_id = request.POST.get('receiver_id')

        # Save the file using Django's storage system
        file_name = default_storage.save(file.name, file)
        file_url = default_storage.url(file_name)

        return JsonResponse({'file_url': file_url, 'filename': file.name})
    return JsonResponse({'error': 'File upload failed'}, status=400)