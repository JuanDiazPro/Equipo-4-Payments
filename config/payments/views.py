from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Payment
from .serializers import PaymentSerializer, ProcessPaymentSerializer
from .services import get_order, update_order_status


@api_view(["POST"])
def process_payment(request):
    input_serializer = ProcessPaymentSerializer(data=request.data)
    input_serializer.is_valid(raise_exception=True)
    validated = input_serializer.validated_data

    order_id = validated["order_id"]
    user_id = validated["user_id"]
    card_number = validated["card_number"]
    expiration_date = validated["expiration_date"]
    cvv = validated["cvv"]

    # 1. Obtener pedido desde Order Service
    order_response = get_order(order_id)

    if not order_response["success"]:
        if order_response["error"] == "not_found":
            return Response(
                {"error": "Pedido no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"error": "El servicio de pedidos no responde correctamente"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    order = order_response["data"]

    order_status = str(order.get("status", "")).lower()
    if order_status == "pagado":
        return Response(
            {"error": "El pedido ya fue pagado"},
            status=status.HTTP_409_CONFLICT,
        )

    if order_status == "enviado":
        return Response(
            {"error": "No se puede cobrar un pedido enviado"},
            status=status.HTTP_409_CONFLICT,
        )

    order_user_id = order.get("user_id", order.get("user"))
    if order_user_id is not None and str(order_user_id) != str(user_id):
        return Response(
            {"error": "El usuario no coincide con el pedido"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    total = order.get("total")
    if total is None:
        return Response(
            {"error": "El pedido no contiene el total a cobrar"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # 2. Simular pago exitoso
    payment = Payment.objects.create(
        order_id=order_id,
        user_id=user_id,
        total=total,
        card_number=card_number,
        card_last4=card_number[-4:],
        expiration_date=expiration_date,
        cvv=cvv,
        status=Payment.PaymentStatus.COMPLETED,
    )

    # 3. Actualizar estado del pedido a "PAGADO"
    update_response = update_order_status(order_id, "PAGADO")

    if not update_response["success"]:
        return Response(
            {
                "warning": "Pago procesado, pero no se pudo actualizar el pedido a Pagado",
                "payment_id": payment.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )

    serializer = PaymentSerializer(payment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)