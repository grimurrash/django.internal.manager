from django.contrib import admin
from eventregistration.models import *


class EventAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'slug', 'is_save_google_table', 'is_send_registration_mail_notification',
        'support_email_address'
    )
    search_fields = ('id', 'name', 'slug')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


class ShiftAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'shift_start_date', 'shift_end_date', 'event')
    search_fields = ('id', 'name', 'event')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'min', 'max', 'event')
    search_fields = ('id', 'name', 'max', 'max', 'event')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


class DirectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'event')
    search_fields = ('id', 'name', 'event')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


class EventLimitAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'limit', 'free_seats', 'shift', 'direction', 'age_group')
    search_fields = ('id', 'event', 'shift', 'direction', 'age_group')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'event', 'is_have_checkbox', 'checkbox_text', 'is_upload', 'show_conditions')
    search_fields = ('id', 'name', 'event')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'surname', 'first_name', 'last_name', 'date_of_birth', 'email', 'event', 'shift', 'age_group', 'direction'
    )
    search_fields = (
        'id', 'surname', 'first_name', 'last_name', 'date_of_birth', 'email', 'event', 'shift', 'age_group', 'direction'
    )
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


admin.site.register(Event, EventAdmin)
admin.site.register(Documents, DocumentAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(AgeGroup, AgeGroupAdmin)
admin.site.register(Direction, DirectionAdmin)
admin.site.register(EventLimit, EventLimitAdmin)
admin.site.register(Participant, ParticipantAdmin)
