from django.contrib import admin
from .models import Vendor, Menu, Client,Order

admin.site.register(Vendor)
admin.site.register(Client)
admin.site.register(Order)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'vendor', 'image')


