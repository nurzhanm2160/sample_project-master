from pprint import pprint

import subprocess


# if you want output
proc = subprocess.Popen("php /usr/src/web/paykassa/api/create_order/index.php", shell=True, stdout=subprocess.PIPE)
script_response = proc.stdout.read()

print('-------------------------------')
print('-------------------------------')
pprint(script_response)
print('-------------------------------')
print('-------------------------------')
# web/paykassa/api/create_order/index.php
# import requests

# defining the api-endpoint
# API_ENDPOINT = "web/paykassa/api/create_order/index.php"
#
# # data to be sent to api
# data = {
#     "amount": 1,
#     "currency": "XRP",
#     "comment": "comment",
#     "paid_commission": "shop"
# }
#
# # sending post request and saving response as response object
# r = requests.post(url=API_ENDPOINT, data=data)
#
# print('----------------------')
# print('----------------------')
# pprint(r)
# print('----------------------')
# print('----------------------')
#
# # from coin.models import Coin, CoinWallet, CoinPrice, Deposit, Plan, RewardFee
# #
# # from authentication.models import User
# #
# # for i in User.objects.all():
# #     print('---------------------------------------')
# #     pprint(f"{i.email} - {i.marketing_source}")
