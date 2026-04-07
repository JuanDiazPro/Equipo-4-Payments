from django.urls import path
from .views import process_payment

urlpatterns = [
    path('payments/process/', process_payment, name='process-payment'),
]