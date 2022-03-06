from django.contrib import admin
from eventtimeline.models import TimelineEvent


class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_name', 'description', 'event_date', 'tags')
    search_fields = ('event_name', 'description', 'event_date', 'tags')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


admin.site.register(TimelineEvent, TimelineEventAdmin)
