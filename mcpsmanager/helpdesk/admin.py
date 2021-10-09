from django.contrib import admin

from .models import Employee, Message

admin.site.register(Employee)
admin.site.register(Message)
