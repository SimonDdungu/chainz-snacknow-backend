from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Restaurant, MenuItem, Order, OrderItem, Cart, CartItem, Transaction


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'password', 'email', 'address', 'phone_number', 'is_customer']
        read_only_fields = ['id', 'is_customer']
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = get_user_model()(**validated_data)
        user.set_password(password) 
        user.save()
            
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'email', 'address', 'phone_number', 'is_customer']
        read_only_fields = ['id', 'is_customer']

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'location', 'description', 'profile_picture','created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class MenuItemSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'restaurant', 'name', 'category', 'price', 'description', 'image', 'available', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'menu_item_name', 'quantity', 'ordered_price', 'subtotal']
        read_only_fields = ['id', 'ordered_price', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'payment_method', 'orderitems', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'total_price', 'created_at', 'updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'menu_item', 'menu_item_name', 'quantity', 'subtotal']
        read_only_fields = ['id', 'subtotal']

class CartSerializer(serializers.ModelSerializer):
    cartitems = CartItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'total_price', 'cartitems', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'total_price', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'order', 'order_id', 'amount_due', 'payment_method', 'status', 'user', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'order_id', 'amount_due', 'user', 'items', 'created_at', 'updated_at']