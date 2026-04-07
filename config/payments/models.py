from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        COMPLETED = "Completed", "Completed"
        FAILED = "Failed", "Failed"

    order_id = models.PositiveIntegerField()
    user_id = models.PositiveIntegerField()
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    card_number = models.CharField(max_length=16)
    # Solo se almacenan los últimos 4 dígitos para referencia segura.
    card_last4 = models.CharField(max_length=4)
    expiration_date = models.CharField(max_length=5)
    cvv = models.CharField(max_length=3)

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - Order {self.order_id}"