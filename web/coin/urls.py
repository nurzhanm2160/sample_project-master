from django.urls import path
from .views import get_balance, cash_out, generate_address, get_payment_url

urlpatterns = [
	path('get_balance', get_balance, name="get balance"),
	path('cashout', cash_out, name="cash out"),
	path('generate_address', generate_address, name="generate address"),
	path('get_payment_url', get_payment_url, name="get payment url"),
]