# from pprint import pprint
# from paykassa.payment import PaymentApi
# from paykassa.dto import CheckBalanceRequest
# from paykassa.struct import System, Currency
#
# client = PaymentApi("20460", "ebeaee9e606a5bf5db5ff7ef6afb49eabc74747fe709889e2692b074bfdd2966")
#
# request = CheckBalanceRequest() \
#     .set_shop("123")
#
# response = client.check_balance(request)
#
# print('----------------------------')
# pprint(response.__dict__)
# print('----------------------------')
#
# if not response.has_error():
#     print(response.get_balance(System.BITCOIN, Currency.BTC))
#     print(response.get_balance(System.ETHEREUM, Currency.ETH))
#
# from paykassa.dto import MakePaymentRequest
# from paykassa.struct import System, Currency, CommissionPayer, TransactionPriority
#
# request = MakePaymentRequest() \
#     .set_shop("123") \
#     .set_amount(1.02) \
#     .set_priority(TransactionPriority.MEDIUM) \
#     .set_system(System.BITCOIN) \
#     .set_currency(Currency.BTC) \
#     .set_paid_commission(CommissionPayer.SHOP) \
#     .set_number("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy")
#
# response = client.make_payment(request)
# print('----------------------------')
# pprint(response.__dict__)
# print('----------------------------')
#
# if not response.has_error():
#     print(response.get_transaction())
#     print(response.get_paid_commission())
#
