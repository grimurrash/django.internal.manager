from django.contrib import admin

from vesnapobed.models import RegistrationMember


class VesnaPobedAdmin(admin.ModelAdmin):
    list_display = ('id', 'surname', 'first_name', 'last_name', 'age', 'school', 'documents_link')
    search_fields = ('surname', 'first_name', 'last_name', 'school')
    filter_horizontal = ()
    list_filter = ('direction', 'age_group', 'shift')
    fieldsets = ()
    ordering = ('-id',)


admin.site.register(RegistrationMember, VesnaPobedAdmin)