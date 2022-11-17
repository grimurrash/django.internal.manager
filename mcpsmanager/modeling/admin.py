from django.contrib import admin
from modeling.models import *


class ShipTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


class ShopModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_name')
    search_fields = ('id', 'model_name')
    filter_horizontal = ()
    list_filter = ('model_type',)
    fieldsets = ()
    ordering = ('-id',)


admin.site.register(ShipType, ShipTypeAdmin)
admin.site.register(ShipModel, ShopModelAdmin)
