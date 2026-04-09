from django.urls import path
from .views import list_payments, payment_detail, process_payment

urlpatterns = [
    path('payments/', list_payments, name='list-payments'),
    path('payments/<int:payment_id>/', payment_detail, name='payment-detail'),
    path('payments/process/', process_payment, name='process-payment'),
]