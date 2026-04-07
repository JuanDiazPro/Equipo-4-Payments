from decimal import Decimal

from django.db import migrations, models
from django.core.validators import MinValueValidator
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="card_last4",
            field=models.CharField(default="0000", max_length=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="payment",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="payment",
            name="order_id",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.CharField(
                choices=[("Pending", "Pending"), ("Completed", "Completed"), ("Failed", "Failed")],
                default="Pending",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="total",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="user_id",
            field=models.PositiveIntegerField(),
        ),
    ]