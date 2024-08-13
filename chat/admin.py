from django.contrib import admin
from .models import NewUser, Room, Message

admin.site.register(NewUser)
admin.site.register(Room)
admin.site.register(Message)
