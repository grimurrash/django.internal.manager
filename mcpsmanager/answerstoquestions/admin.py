from django.contrib import admin
from answerstoquestions.models import Question


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'yes_answer_name', 'no_answer_name', 'yes_answer', 'no_answer')
    search_fields = ('id', 'question')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


admin.site.register(Question, QuestionAdmin)
