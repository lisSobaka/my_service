from django.contrib import admin
from .models import Employees


class RepairersAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'first_name', 'last_name', 'is_active', 'percent')
    list_display_links = ('pk', )
    list_editable = ('is_active', 'percent')


admin.site.register(Employees, RepairersAdmin)