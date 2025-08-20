from django.db import models

from apps.commerce.models import Cart
from apps.product.models import Product


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="cart_entries")
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cart} - {self.product} ({self.quantity})"

    class Meta:
        db_table = "cart_item"
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["cart", "product"], name="unique_product_in_cart")]
