from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from paykassa.payment import PaymentApi
from paykassa.dto import CheckBalanceRequest, MakePaymentRequest
from paykassa.struct import System, Currency, CommissionPayer, TransactionPriority 

from paykassa.merchant import MerchantApi
from paykassa.dto import GenerateAddressRequest, GetPaymentUrlRequest
from paykassa.struct import System, Currency, CommissionPayer

from .check_payment_system import check_payment_system
from .check_payment_currency import check_payment_currency



# client instance. 
# 1-st parametr merchant id
# 2-nd parametr api key

client = PaymentApi(21855, "fqUUyP5ZX6JcCt798TjTsmFFqG8slXz7") 

@api_view(['GET'])
def test(request):
	return Response({"message": "представление работает"})

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
		.set_paid_commission(CommissionPayer.CLIENT)

	response = client.generate_address(generate_address_request)

	if not response.has_error():
		print(response.get_amount())
		print(response.get_wallet())
		return Response({"amount": response.get_amount(), "wallet": response.get_wallet()})
		
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
		.set_paid_commission(CommissionPayer.CLIENT)

	response = client.get_payment_url(get_payment_request)

	if not response.has_error():
		print(response.get_method())
		print(response.get_url())
		return Response({"method": response.get_method(), "url": response.get_url()})

	return Response({"message": response.get_message()})



