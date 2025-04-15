# models.py
from django.db import models
from django.contrib.auth.models import User
from store.models import Product  # Assuming Product model exists in the 'store' app

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    # Method to calculate the total price of the cart
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    # Method to calculate the total price for this CartItem (price * quantity)
    def total_price(self):
        return self.product.price * self.quantity
