from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Payment


class ProcessPaymentTests(APITestCase):
    def setUp(self):
        self.url = reverse("process-payment")
        self.payload = {
            "order_id": 100,
            "user_id": 50,
            "card_number": "4111111111111111",
            "expiration_date": "12/30",
            "cvv": "123",
        }

    @patch(
        "payments.views.update_order_status",
        return_value={
            "success": True,
            "error": None,
            "status_code": 200,
        },
    )
    @patch("payments.views.get_order")
    def test_process_payment_success(self, mock_get_order, _mock_update_order_status):
        mock_get_order.return_value = {
            "success": True,
            "data": {
                "id": 100,
                "user_id": 50,
                "status": "Pendiente",
                "total": "999.99",
            },
            "error": None,
            "status_code": 200,
        }

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)

        payment = Payment.objects.first()
        self.assertEqual(payment.order_id, 100)
        self.assertEqual(payment.user_id, 50)
        self.assertEqual(payment.card_last4, "1111")
        self.assertEqual(payment.status, Payment.PaymentStatus.COMPLETED)

        self.assertEqual(response.data["card_number"], "**** **** **** 1111")
        self.assertEqual(response.data["cvv"], "***")

    @patch(
        "payments.views.get_order",
        return_value={
            "success": False,
            "data": None,
            "error": "not_found",
            "status_code": 404,
        },
    )
    def test_process_payment_order_not_found(self, _mock_get_order):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Payment.objects.count(), 0)

    @patch(
        "payments.views.get_order",
        return_value={
            "success": False,
            "data": None,
            "error": "connection_error",
            "status_code": 503,
        },
    )
    def test_process_payment_order_service_unavailable(self, _mock_get_order):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(Payment.objects.count(), 0)

    @patch("payments.views.get_order")
    def test_process_payment_rejects_user_mismatch(self, mock_get_order):
        mock_get_order.return_value = {
            "success": True,
            "data": {
                "id": 100,
                "user_id": 999,
                "status": "Pendiente",
                "total": "100.00",
            },
            "error": None,
            "status_code": 200,
        }

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.count(), 0)

    @patch("payments.views.get_order")
    def test_process_payment_rejects_order_already_paid(self, mock_get_order):
        mock_get_order.return_value = {
            "success": True,
            "data": {
                "id": 100,
                "user_id": 50,
                "status": "Pagado",
                "total": "999.99",
            },
            "error": None,
            "status_code": 200,
        }

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Payment.objects.count(), 0)

    @patch("payments.views.get_order")
    def test_process_payment_rejects_order_already_shipped(self, mock_get_order):
        mock_get_order.return_value = {
            "success": True,
            "data": {
                "id": 100,
                "user_id": 50,
                "status": "Enviado",
                "total": "999.99",
            },
            "error": None,
            "status_code": 200,
        }

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Payment.objects.count(), 0)

    @patch("payments.views.get_order")
    def test_process_payment_rejects_when_order_has_no_total(self, mock_get_order):
        mock_get_order.return_value = {
            "success": True,
            "data": {
                "id": 100,
                "user_id": 50,
                "status": "Pendiente",
            },
            "error": None,
            "status_code": 200,
        }

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(Payment.objects.count(), 0)

    def test_process_payment_rejects_invalid_card_format(self):
        invalid_payload = {
            **self.payload,
            "card_number": "4111",
        }

        response = self.client.post(self.url, invalid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.count(), 0)

    @patch(
        "payments.views.update_order_status",
        return_value={
            "success": False,
            "error": "service_error",
            "status_code": 500,
        },
    )
    @patch("payments.views.get_order")
    def test_process_payment_returns_accepted_when_order_not_updated(
        self, mock_get_order, _mock_update_order_status
    ):
        mock_get_order.return_value = {
            "success": True,
            "data": {
                "id": 100,
                "user_id": 50,
                "status": "Pendiente",
                "total": "999.99",
            },
            "error": None,
            "status_code": 200,
        }

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertIn("warning", response.data)
        self.assertIn("payment_id", response.data)