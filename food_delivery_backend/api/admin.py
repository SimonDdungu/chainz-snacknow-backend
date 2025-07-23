from django.contrib import admin
from .models import CustomUser, Restaurant, MenuItem, Order, OrderItem, Cart, CartItem, Transaction

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Transaction)