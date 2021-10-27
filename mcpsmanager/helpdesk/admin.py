from django.contrib import admin

from helpdesk.models import Employee, Message, AccountCategory, Account

admin.site.register(Employee)
admin.site.register(Message)
admin.site.register(AccountCategory)
admin.site.register(Account)
