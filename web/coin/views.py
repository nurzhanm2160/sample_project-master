from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PlanSerializer, TransactionSerializer

from .models import Plan, Transaction
from authentication.models import User

from paykassa.payment import PaymentApi
from paykassa.dto import CheckBalanceRequest, MakePaymentRequest
from paykassa.struct import System, Currency, CommissionPayer, TransactionPriority

from .check_payment_system import check_payment_system
from .check_payment_currency import check_payment_currency

from .paykassa_services import _get_payment_url, _check_payment, _change_transaction_status_to_paid, \
    _get_transaction_by_order_id, _get_fresh_prices_and_calculate_currency_in_usd, _create_user_deposit_and_save, \
    _generate_address, _webhook, _cash_out, _get_days_for_check_payment_amount, _get_user_reward, _get_deposit_object, \
    _clear_reward_after_withdraw, _clear_deposit, _get_all_users, _get_all_deposits, _get_all_withdraws

import pyqrcode
import io
import base64
from datetime import datetime

client = PaymentApi(21855, "fqUUyP5ZX6JcCt798TjTsmFFqG8slXz7")


@api_view(['GET'])
def get_balance(request):
    check_balance_request = CheckBalanceRequest().set_shop("20132")
    response = client.check_balance(check_balance_request)

    if response.has_error():
        return Response({"message": response.get_message()})

    return Response({"balance": response.get_balance(System.BITCOIN, Currency.BTC)})


@api_view(['POST'])
def cash_out(request):
    amount = request.data["amount"]
    system = check_payment_system(request.data["system"])
    currency = check_payment_currency(request.data["currency"])
    number = request.data["number"]
    user_id = request.data["user_id"]

    days = _get_days_for_check_payment_amount(user_id)
    reward = _get_user_reward(user_id, currency)
    deposit = _get_deposit_object(user_id)

    if days.days < deposit.term:
        if amount > reward:
            return Response({'message': 'Сумма больше, чем Вы можете вывести'})
        else:
            _clear_reward_after_withdraw(user_id, currency)
    else:
        _clear_deposit()

    response = _cash_out(amount, system, currency, number, user_id)

    if not response.has_error():
        user = get_object_or_404(User, id=user_id)
        transaction = Transaction()
        transaction.txid = response.get_txid()
        transaction.amount = response.get_amount()
        transaction.amount_pay = response.get_amount_pay()
        transaction.system = response.get_system()
        transaction.currency = response.get_currency()
        transaction.number = response.get_number()
        transaction.transaction_type = 'withdraw'
        transaction.user = user
        transaction.save()

        return Response({
            "transaction": response.get_transaction(),
            "commission": response.get_paid_commission(),
        })

    return Response({"message": response.get_message()})


@api_view(['POST'])
def generate_address(request):
    # varialbles from frontend
    amount = request.data["amount"]
    currency = request.data["currency"]
    system = check_payment_system(request.data["system"])
    comment = request.data["comment"]
    user_id = request.data["user_id"]
    term = request.data['term']

    response = _generate_address(amount=amount,
                                 system=system,
                                 currency=currency,
                                 user_id=user_id,
                                 comment=comment,
                                 term=term)

    if not response.has_error():
        wallet = response.get_wallet()
        qr = pyqrcode.create(f'{wallet}')
        buffer = io.BytesIO()
        qr.png(buffer, scale=6)
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return Response({
            "amount": response.get_amount(),
            "wallet": response.get_wallet(),
            "url": response.get_url()
            # "invoice": response.get_invoice(),
            # "url": response.get_url(),
            # "qr": qr_code_base64
        })

    return Response({"message": response.get_message()})


@api_view(['POST'])
def get_payment_url(request):
    amount = request.data["amount"]
    comment = request.data["comment"]
    system = check_payment_system(request.data["system"])
    currency = check_payment_currency(request.data["currency"])

    response = _get_payment_url(amount=amount, comment=comment, system=system, currency=currency, test="true")

    if not response.has_error():
        print(response.get_method())
        print(response.get_url())
        return Response({"method": response.get_method(), "url": response.get_url(), "params": response.get_params()})

    return Response({"message": response.get_message()})


@api_view(['POST'])
def check_payment(request):
    user_id = request.data['user_id']
    order_id = request.data['order_id']

    transaction = _get_transaction_by_order_id(order_id)
    response = _check_payment(order_id, "true")

    if not response.has_error():
        _change_transaction_status_to_paid(order_id)
        currency = transaction.currency
        amount = transaction.amount
        amount_in_usd = _get_fresh_prices_and_calculate_currency_in_usd(currency, amount)
        _create_user_deposit_and_save(user_id, amount_in_usd)

        return Response({
            "transaction": response.get_transaction(),
            "shop_id": response.get_shop_id(),
            "order_id": response.get_order_id(),
            "amount": response.get_amount(),
            "tag": response.get_tag(),
            "message": response.get_message()
        })

    return Response({"message": response.get_message()})


@api_view(['GET'])
def get_plans(request):
    items = Plan.objects.all()

    if items:
        plans = PlanSerializer(items, many=True)
        return Response({"data": plans.data})
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'GET'])
def process(request):
    print(request.data)
    order_id = request.data['order_id']
    private_hash = request.data['private_hash']
    _webhook(order_id, private_hash)

    return Response({"process": request.data})


@api_view(['POST', 'GET'])
def success(request):
    print(request.data)
    return Response({"success": request.data})


@api_view(['POST', 'GET'])
def fail(request):
    print(request.data)
    return Response({"fail": request.data})


@api_view(['GET'])
def get_all_transactions(request):
    deposits = Transaction.objects.filter(transaction_type="paid")
    print(deposits)
    withdraws = Transaction.objects.filter(transaction_type="withdraw")
    print(withdraws)

    serialized_deposits = TransactionSerializer(deposits, many=True)
    serialized_withdraws = TransactionSerializer(withdraws, many=True)
    return Response({
        "deposits": serialized_deposits.data,
        "withdraws": serialized_withdraws.data
    })


@api_view(['GET'])
def get_all_users(request):
    users = _get_all_users()
    return Response({'users': len(users)})


@api_view(['GET'])
def get_all_deposits(request):
    deposit_sum = _get_all_deposits()
    return Response({'deposit_sum': deposit_sum})


@api_view(['GET'])
def get_all_withdraws(request):
    withdraw_sum = _get_all_withdraws()
    return Response({'withdraw_sum': withdraw_sum})
