from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('user/', views.UserDetailView.as_view(), name='user-detail'),
    path('restaurants/', views.RestaurantListCreateView.as_view(), name='restaurant-list'),
    path('restaurants/<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('menu-items/', views.MenuItemListCreateView.as_view(), name='menu-item-list'),
    path('menu-items/<int:pk>/', views.MenuItemDetailView.as_view(), name='menu-item-detail'),
    path('cart/', views.CartDetailView.as_view(), name='cart-detail'),
    path('cart-items/', views.CartItemListCreateView.as_view(), name='cart-item-list'),
    path('cart-items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    path('orders/', views.OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('order-items/', views.OrderItemListCreateView.as_view(), name='order-item-list'),
    path('order-items/<int:pk>/', views.OrderItemDetailView.as_view(), name='order-item-detail'),
    path('transactions/', views.TransactionListCreateView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
]