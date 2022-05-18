from django.contrib import admin

from museumregistration.models import RegistrationMember


class MuseumRegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'surname', 'first_name', 'last_name', 'date_of_birth', 'school', 'documents_link')
    search_fields = ('surname', 'first_name', 'last_name', 'school')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


admin.site.register(RegistrationMember, MuseumRegistrationAdmin)
