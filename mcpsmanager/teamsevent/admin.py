from django.contrib import admin

from teamsevent.models import TeamsEvent, Group, Member

admin.site.register(TeamsEvent)
admin.site.register(Group)
admin.site.register(Member)