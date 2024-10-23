# in chat/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    store_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Seller: {self.user.username} - {self.store_name}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Customer: {self.user.username}"
    
    
# chat/models.py
from django.db import models
from django.conf import settings

class Chat(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_seller', limit_choices_to={'is_seller': True})
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_customer', limit_choices_to={'is_customer': True})
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seller', 'customer')  # Ensure one unique chat per seller-customer pair


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure sender is either the seller or customer in this chat
        if self.sender != self.chat.seller and self.sender != self.chat.customer:
            raise ValueError("Sender must be either the seller or the customer in this chat.")
        super().save(*args, **kwargs)
