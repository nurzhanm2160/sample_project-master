from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .serializers import PlanSerializer

from .models import Plan

from paykassa.payment import PaymentApi
from paykassa.merchant import MerchantApi
from paykassa.dto import GenerateAddressRequest, GetPaymentUrlRequest, CheckBalanceRequest
from paykassa.struct import System, Currency, CommissionPayer, TransactionPriority 

from .check_payment_system import check_payment_system
from .check_payment_currency import check_payment_currency
from .get_payment_details import get_payment_details

import pyqrcode
import io
import base64


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
	number = check_payment_number(request.data["number"])

	make_payment_request = MakePaymentRequest() \
	.set_shop("20132") \
	.set_amount(amount) \
	.set_priority(TransactionPriority.MEDIUM) \
	.set_system(system) \
	.set_currency(currency) \
	.set_paid_commission(CommissionPayer.SHOP) \
	.set_number(number) \
	.set_test(True) # Mock payment

	response = client.make_payment(make_payment_request)

	if not response.has_error():
		print(response.get_transaction())
		print(response.get_paid_commission())
		return Response({"transaction": response.get_transaction(), "commission": response.get_paid_commission()})

	return Response({"message": response.get_message()})

@api_view(['POST'])
def generate_address(request):
	client = MerchantApi(20132, "8x6GobG05RMhUTwwLNEU879oNZNTeWz6")


	# varialbles from frontend 
	amount = request.data["amount"]
	currency = request.data["currency"]
	system = check_payment_system(request.data["system"])
	comment = request.data["comment"]

	generate_address_request = GenerateAddressRequest() \
		.set_amount(amount) \
		.set_currency(Currency.DOGE) \
		.set_system(system) \
		.set_comment(comment) \
		.set_paid_commission(CommissionPayer.CLIENT) \
		# .set_test(True)

	response = client.generate_address(generate_address_request)

	wallet = response.get_wallet()
	qr = pyqrcode.create(f'{wallet}')
	buffer = io.BytesIO()
	qr.png(buffer, scale=6)
	qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

	if not response.has_error():
		print(response.get_amount())
		print(response.get_wallet())
		return Response({
			"amount": response.get_amount(), 
			"wallet": response.get_wallet(),
			"invoice": response.get_invoice(),
			"url": response.get_url(),
			"qr": qr_code_base64
			})
		
	return Response({"message": response.get_message()})


@api_view(['POST'])
def get_payment_url(request):
	client = MerchantApi(20132, "8x6GobG05RMhUTwwLNEU879oNZNTeWz6")

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
		.set_test(True)

	response = client.get_payment_url(get_payment_request)


	if not response.has_error():
		print(response.get_method())
		print(response.get_url())
		return Response({"method": response.get_method(), "url": response.get_url(), "params": response.get_params()})

	return Response({"message": response.get_message()})

@api_view(['GET']) # TODO: change this to POST method
def check_payment(request):
	client = MerchantApi(20132, "8x6GobG05RMhUTwwLNEU879oNZNTeWz6")

	check_payment_request = CheckPaymentRequest()\
		.set_private_hash("ba276492c1c8ff5bfad7ea46463aca85d9c447ee940aceeb71e4a726d89458cd")

	response = client.check_payment(check_payment_request)

	if not response.has_error():
		return Response({
			"transaction": response.get_transaction(),
			"shop_id": response.get_shop_id(),
			"order_id": response.get_order_id(),
			"amount": response.get_amount(),
			"currency": response.get_currency(),
			"system": response.get_system(),
			"address": response.get_address(),
			"tag": response.get_tag(),
			"hash": response.get_hash(),
			"is_partial": response.is_partial()
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
