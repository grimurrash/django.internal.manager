from django.contrib import admin
from surveysmanager.models import *


class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id',  'name', 'url')
    search_fields = ('id', 'name', 'url')
    filter_horizontal = ()
    fieldsets = ()
    ordering = ('-id',)


class SurveyAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey')
    search_fields = ('id', 'survey')
    filter_horizontal = ()
    fieldsets = ()
    ordering = ('-id',)


admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyAnswer, SurveyAnswerAdmin)