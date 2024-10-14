from django.contrib import admin
from botadvisorsmcvp.models import *


class InterviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'chat_id', 'step', 'questing_step', 'questing_balls', 'is_need_send', 'is_send_final_message', 'video_url'
    )
    search_fields = ('chat_id', 'interview_answers')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


admin.site.register(Interview, InterviewAdmin)
