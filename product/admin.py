from .models import Product, Customer, Order, OrderItem, ShippingAddress
from django.contrib import admin
admin.site.site_header = "Souq.com"
admin.site.site_title = "Administration" 

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order','product','quantity',)

class orderLineItem(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'complete','date_ordered',)
    inlines = [orderLineItem]
    



class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('customer','address','city','state')

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)

