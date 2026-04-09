from datetime import datetime
from rest_framework import serializers
from .models import Payment


class ProcessPaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    user_id = serializers.IntegerField(min_value=1)
    card_number = serializers.RegexField(
        regex=r"^\d{16}$",
        error_messages={
            "invalid": "El número de tarjeta debe contener exactamente 16 dígitos."
        }
    )
    expiration_date = serializers.RegexField(
        regex=r"^(0[1-9]|1[0-2])\/\d{2}$",
        error_messages={
            "invalid": "La fecha de expiración debe tener el formato MM/YY."
        }
    )
    cvv = serializers.RegexField(
        regex=r"^\d{3}$",
        error_messages={
            "invalid": "El CVV debe contener exactamente 3 dígitos."
        }
    )

    def validate_expiration_date(self, value):
        """
        Valida que la tarjeta no esté vencida.
        Formato esperado: MM/YY
        """
        month, year = value.split("/")
        month = int(month)
        year = int(f"20{year}")

        now = datetime.now()
        current_year = now.year
        current_month = now.month

        if year < current_year or (year == current_year and month < current_month):
            raise serializers.ValidationError("La tarjeta está vencida.")

        return value


class PaymentSerializer(serializers.ModelSerializer):
    card_number = serializers.SerializerMethodField()
    cvv = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "user_id",
            "total",
            "card_number",
            "card_last4",
            "expiration_date",
            "cvv",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "total",
            "card_last4",
            "status",
            "created_at",
            "updated_at",
        ]

    def get_card_number(self, obj):
        if not obj.card_last4:
            return None
        return f"**** **** **** {obj.card_last4}"

    def get_cvv(self, obj):
        if not obj.cvv:
            return None
        return "***"