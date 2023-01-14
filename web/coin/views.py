from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .serializers import PlanSerializer, TransactionSerializer

from .models import Plan, Transaction, Deposit, Coin
from authentication.models import User

from paykassa.payment import PaymentApi
from paykassa.merchant import MerchantApi
from paykassa.dto import GenerateAddressRequest, GetPaymentUrlRequest, CheckBalanceRequest, MakePaymentRequest, CheckTransactionRequest, CheckPaymentRequest
from paykassa.struct import System, Currency, CommissionPayer, TransactionPriority 

from .check_payment_system import check_payment_system
from .check_payment_currency import check_payment_currency
from .get_payment_details import get_payment_details

import pyqrcode
import io
import base64
from datetime import datetime


# client instance. 
# 1-st parametr merchant id
# 2-nd parametr api key

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

	# varialbles from frontend 
	amount = request.data["amount"]
	system = check_payment_system(request.data["system"])
	currency = check_payment_currency(request.data["currency"])
	number = request.data["number"]
	user_id = request.data["user_id"]

	make_payment_request = MakePaymentRequest() \
	.set_shop("20265") \
	.set_amount(amount) \
	.set_priority(TransactionPriority.MEDIUM) \
	.set_system(system) \
	.set_currency(currency) \
	.set_paid_commission(CommissionPayer.SHOP) \
	.set_number(number) \
	.set_test("true") \

	response = client.make_payment(make_payment_request)

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
	client = MerchantApi(20265, "JAVo1wzFOu2F5A1xCDsTMsCMhLwUmLoV")

	# varialbles from frontend 
	amount = request.data["amount"]
	currency = request.data["currency"]
	system = check_payment_system(request.data["system"])
	comment = request.data["comment"]
	user_id = request.data["user_id"]


	user = get_object_or_404(User, id=user_id)
	transactions = Transaction.objects.filter(~Q(payment_id=0))
	order_id = len(transactions) + 1
	transaction = Transaction(payment_id=order_id, amount=amount, system=system, currency=currency)

	transaction.user = user
	transaction.save()
	user.save()

	generate_address_request = GenerateAddressRequest() \
		.set_order_id(order_id) \
		.set_amount(amount) \
		.set_currency(Currency.DOGE) \
		.set_system(system) \
		.set_comment(comment) \
		.set_paid_commission(CommissionPayer.CLIENT) \
		.set_test("true")

	response = client.generate_address(generate_address_request)



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
	client = MerchantApi(20265, "JAVo1wzFOu2F5A1xCDsTMsCMhLwUmLoV")

	# varialbles from frontend 
	amount = request.data["amount"]
	comment = request.data["comment"]
	system = check_payment_system(request.data["system"])
	currency = check_payment_currency(request.data["currency"])

	get_payment_request = GetPaymentUrlRequest() \
		.set_amount(amount) \
		.set_currency(currency) \
		.set_system(system) \
		.set_comment(comment) \
		.set_paid_commission(CommissionPayer.CLIENT) \
		.set_test("true")

	response = client.get_payment_url(get_payment_request)


	if not response.has_error():
		print(response.get_method())
		print(response.get_url())
		return Response({"method": response.get_method(), "url": response.get_url(), "params": response.get_params()})

	return Response({"message": response.get_message()})

@api_view(['POST'])
def check_payment(request):
	client = MerchantApi(20265, "JAVo1wzFOu2F5A1xCDsTMsCMhLwUmLoV")

	user_id = request.data['user_id']
	order_id = request.data['order_id']

	transaction = get_object_or_404(Transaction, payment_id=order_id)
	private_hash = transaction.private_hash

	check_payment_request = CheckPaymentRequest()\
		.set_private_hash('37827c98289d857eee8a7bba3f14be0778fbca4b0f3700d81a7df1b8cfc85183') \
		.set_test("true")

	response = client.check_payment(check_payment_request)

	if not response.has_error():
		transaction.transaction_type = 'paid'
		transaction.save()
		currency = transaction.currency
		amount_in_usd = 0


		BTC = get_object_or_404(Coin, ticker='BTC') 
		LTC = get_object_or_404(Coin, ticker='LTC') 
		TRX = get_object_or_404(Coin, ticker='TRX') 
		ETH = get_object_or_404(Coin, ticker='ETH') 


		if(currency == 'DOGE'):
			amount_in_usd = float(transaction.amount) * float(0.086)
		elif(currency == 'BTC'):
			amount_in_usd = float(transaction.amount) * BTC.current_price
		elif(currency == 'LTC'):
			amount_in_usd = float(transaction.amount) * LTC.current_price
		elif(currency == 'TRX'):
			amount_in_usd = float(transaction.amount) * TRX.current_price
		elif(currency == 'ETH'):
			amount_in_usd = float(transaction.amount) * ETH.current_price

		user = get_object_or_404(User, id=user_id)
		print(user)

		deposit = Deposit(owner=user, deposit_amount_in_usd=amount_in_usd, datetime_moment=datetime.now())
		deposit.save()
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

	if(items):
		plans = PlanSerializer(items, many=True)
		return Response({"data": plans.data})
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'GET'])
def process(request):
	print(request.data)
	order_id = request.data['order_id']
	private_hash = request.data['private_hash']

	transaction = get_object_or_404(Transaction, payment_id=order_id)
	transaction.transaction_type = 'paid'
	transaction.private_hash = private_hash
	transaction.save()

	currency = transaction.currency
	amount_in_usd = 0


	BTC = get_object_or_404(Coin, ticker='BTC') 
	LTC = get_object_or_404(Coin, ticker='LTC') 
	TRX = get_object_or_404(Coin, ticker='TRX') 
	ETH = get_object_or_404(Coin, ticker='ETH') 


	if(currency == 'DOGE'):
		amount_in_usd = float(transaction.amount) * float(0.086)
	elif(currency == 'BTC'):
		amount_in_usd = float(transaction.amount) * BTC.current_price
	elif(currency == 'LTC'):
		amount_in_usd = float(transaction.amount) * LTC.current_price
	elif(currency == 'TRX'):
		amount_in_usd = float(transaction.amount) * TRX.current_price
	elif(currency == 'ETH'):
		amount_in_usd = float(transaction.amount) * ETH.current_price

	user_id = transaction.user_id
	deposit = Deposit(owner_id=user_id, deposit_amount_in_usd=amount_in_usd, datetime_moment=datetime.now())
	deposit.save()

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

	serilized_deposits = TransactionSerializer(deposits, many=True)
	serialized_withdraws = TransactionSerializer(withdraws, many=True)
	return Response({
		"deposits": serilized_deposits.data,
		"withdraws": serialized_withdraws.data
	})