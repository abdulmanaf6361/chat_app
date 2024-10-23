# chat/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    is_seller = forms.BooleanField(required=False, label='Register as Seller')
    is_customer = forms.BooleanField(required=False, label='Register as Customer')

    class Meta:
        model = User
        fields = ['username', 'email', 'is_seller', 'is_customer', 'password1', 'password2']
