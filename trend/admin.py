from django.contrib import admin
from trend import models


class ValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'change', 'sensor')
    list_filter = ('sensor',)


class TrendAdmin(admin.ModelAdmin):
    list_display = ('number', 'location')
    list_filter = ('location',)


admin.site.register(models.Value, ValueAdmin)
admin.site.register(models.Trend, TrendAdmin)
admin.site.register(models.Sensor)
admin.site.register(models.Location)
admin.site.register(models.PLC)



