from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Restaurant, MenuItem, Order, OrderItem, Cart, CartItem, Transaction
from .serializers import RegisterUserSerializer, CustomUserSerializer, RestaurantSerializer, MenuItemSerializer, OrderSerializer, OrderItemSerializer, CartSerializer, CartItemSerializer, TransactionSerializer
from rest_framework_simplejwt.tokens import RefreshToken


# User Registration
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)

        if serializer.is_valid():
           user = serializer.save()
           refresh = RefreshToken.for_user(user)
           return Response({
                "message": "User created",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# User Detail
class UserDetailView(RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user
    


# Restaurant Views
class RestaurantListCreateView(ListCreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RestaurantDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]
    
    


# MenuItem Views
class MenuItemListCreateView(ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []
    
    def perform_create(self, serializer):
        restaurant = serializer.validated_data['restaurant']
        if restaurant.user != self.request.user:
            raise serializer.ValidationError("You can only add items to your own restaurant")
        serializer.save()

class MenuItemDetailView(RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return []
    
class CategoriesView(APIView):
     authentication_classes = []
     def get(self, request):
        categories = [{'category': key, 'label': label} for key, label in MenuItem.Category]
        return Response(list(categories))
    
class CategoriesViewItems(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, category):
        # Filter menu items by category
        items = MenuItem.objects.filter(category=category)
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)


# Cart Views
class CartDetailView(RetrieveUpdateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return Cart.objects.get(user=self.request.user)

class CartItemListCreateView(ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    def perform_create(self, serializer):
        cart = Cart.objects.get(user=self.request.user)
        serializer.save(cart=cart)

class CartItemDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    
    
    
    
    

# Order Views
class OrderListCreateView(ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderDetailView(RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderItemListCreateView(ListCreateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)
    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        if order.user != self.request.user:
            raise serializer.ValidationError("You can only add items to your own order")
        serializer.save()

class OrderItemDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)
    
    
    
    
    
    
    

# Transaction Views
class TransactionListCreateView(ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        if order.user != self.request.user:
            raise serializer.ValidationError("You can only create transactions for your own orders")
        serializer.save(user=self.request.user)

class TransactionDetailView(RetrieveUpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
