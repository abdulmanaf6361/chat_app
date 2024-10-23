from django.contrib import admin

# Register your models here.
from main.models import *

admin.site.register(User)
admin.site.register(Chat)
admin.site.register(Customer)
admin.site.register(Seller)
admin.site.register(Message)