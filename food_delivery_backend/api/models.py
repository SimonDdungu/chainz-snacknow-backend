from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_customer = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        if self.email:  
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Restaurant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_restaurants")
    name = models.CharField(max_length=255, unique=True)
    profile_picture = models.ImageField(upload_to="restaurants/profilepictures/", blank=True, null=True)
    location = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    

class MenuItem(models.Model):

    Category = [
        ("appetizer", "Appetizer"),
        ("main_course", "Main Course"),
        ("side_dish", "Side Dish"),
        ("dessert", "Dessert"),
        ("beverage", "Beverage"),
        ("kids_menu", "Kids Menu"),
    ]
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="restaurant_menuitems")
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category, default="main_course")
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
    )
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="images/menu/", null=True, blank=True)
    available = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ['restaurant', 'name']

    def __str__(self):
        return self.name


class Order(models.Model):
    # pending - stored in db / Pending - what user sees
    PaymentMethods = [
        ("cash", "Cash"),
        ("debit_card", "Debit Card"),
        ("mobile_money", "Mobile Money"),
        ("paypal", "PayPal"),
    ]

    Status = [
        ("pending", "Pending"),
        ("ready", "Ready"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(max_length=20, choices=Status, default="pending")
    total_price = models.DecimalField(
        max_digits=7, decimal_places=2, validators=[MinValueValidator(0.00)]
    )
    payment_methods = models.CharField(
        max_length=20, choices=PaymentMethods, default="mobile_money"
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total_price(self):
        return sum(item.subtotal for item in self.orderitems.all())

    def save(self):
        self.total_price = self.calculate_total_price()
        super().save()

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return f"Order {self.id} by {self.user.username} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="orderitems", on_delete=models.CASCADE
    )
    menu_item = models.ForeignKey(
        MenuItem, related_name="order_menuitems", on_delete=models.SET_NULL, null=True
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    ordered_price = models.DecimalField(
        max_digits=7, decimal_places=2, validators=[MinValueValidator(0.00)]
    )

    def save(self):
        if self.menu_item:
            self.ordered_price = self.menu_item.price
        super().save()

    @property
    def subtotal(self):
        return self.quantity * self.ordered_price

    class Meta:
        ordering = ["-order__created_at"]

    def __str__(self):
        # 5x Burgers - Order 22
        return f"{self.quantity}x {self.menu_item.name} - Order #{self.order.id}"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_cart")
    total_price = models.DecimalField(
        max_digits=7, decimal_places=2, validators=[MinValueValidator(0.00)]
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total_price(self):
        return sum(item.subtotal for item in self.cartitems.all())

    def save(self):
        self.total_price = self.calculate_total_price()
        super().save()

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return f"Cart {self.id} by {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cartitems")
    menu_item = models.ForeignKey(
        MenuItem, related_name="cart_menuitems", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    @property
    def subtotal(self):
        return self.quantity * self.menu_item.price

    def save(self):
        super().save()
        self.cart.save() # update cart with any updates that might happen such as price changes.
        
    def delete(self):
        this_cart = self.cart # we first assign the cart becoz it might not exist after delete yet we need it to update the Cart model.
        super().delete()
        this_cart.save() #Update Cart with deleted item

    class Meta:
        ordering = ["-cart__updated_at"]

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} - Cart #{self.cart.id}"


class Transaction(models.Model):
    Status = [
        ("success", "Success"),
        ("failed", "Failed"),
        ("pending", "Pending"),
    ]
    order = models.ForeignKey(Order, related_name="transactions", on_delete=models.SET_NULL, null=True)
    ordered_id = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    amount_due = models.DecimalField(decimal_places=2, max_digits=7, validators=[MinValueValidator(0.00)])
    payment_method = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=Status, default="pending")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_transactions"
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self):
        if not self.pk and self.order:
            self.order_id = self.order.id
            self.amount_due = self.order.total_price
            self.payment_method = self.order.payment_methods
            self.user = self.order.user.id
        super().save()
        

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Transaction {self.id} - Order ID {self.order_id} on {self.created_at}"
