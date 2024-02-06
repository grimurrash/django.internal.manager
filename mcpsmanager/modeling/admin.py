from django.contrib import admin
from modeling.models import *


class ShipTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ('-id',)


class ShipModelFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'ship_model_id')
    search_fields = ('id', 'ship_model_id')
    filter_horizontal = ()
    list_filter = ('ship_model_id',)
    fieldsets = ()
    ordering = ('-id',)

class ModelInline(admin.TabularInline):
    model = ShipModelFile

class ShipModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_name')
    search_fields = ('id', 'model_name')
    filter_horizontal = ()
    list_filter = ('model_type',)
    fieldsets = ()
    ordering = ('-id',)
    inlines = [ModelInline]

admin.site.register(ShipType, ShipTypeAdmin)
admin.site.register(ShipModel, ShipModelAdmin)
admin.site.register(ShipModelFile, ShipModelFileAdmin)
