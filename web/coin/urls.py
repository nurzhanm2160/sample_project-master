from django.urls import path
from .views import *


urlpatterns = [
    path('get_balance/', get_balance, name="get balance"),
    path('cashout/', cash_out, name="cash out"),
    path('generate_address/', generate_address, name="generate address"),
    path('get_payment_url/', get_payment_url, name="get payment url"),
    path('check_payment/', check_payment, name="check payment"),
    path('get_plans/', get_plans, name="get plans"),
    path('process/', process, name="paykassa process"),
    path('success', success, name="paykassa success"),
    path('fail/', fail, name="paykassa fail"),
    path('transactions/', get_all_transactions, name="get all transactions"),
    path('get_users/', get_all_users, name='get all users'),
    path('get_all_withdraws/', get_all_withdraws, name='get all withdraws'),
    path('get_all_deposits/', get_all_deposits, name='get all deposits')
]
