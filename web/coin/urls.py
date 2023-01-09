from django.urls import path
from .views import get_balance, cash_out, generate_address, get_payment_url, check_payment, get_plans

urlpatterns = [
	path('get_balance', get_balance, name="get balance"),
	path('cashout', cash_out, name="cash out"),
	path('generate_address', generate_address, name="generate address"),
	path('get_payment_url', get_payment_url, name="get payment url"),
	path('check_payment', check_payment, name="check payment"),
	path('get_plans', get_plans, name="get plans")
]