from rest_framework import serializers
from .models import Plan, Transaction, Deposit

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['title', 'percent_per_day']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['txid', 'payment_id', 'amount', 'amount_pay', 'system', 'currency', 'number', 'transaction_type']

class DepositSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ['owner', 'deposit_amount_in_usd', 'datetime_moment']