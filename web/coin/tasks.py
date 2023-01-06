# Create your tasks here

from .models import Coin, CoinWallet
from src.celery import app


@app.task(name='add_fresh_price')
def add_fresh_price():
    if Coin.objects.count()>0:
        for coin in Coin.objects.all():
            coin.get_newest_price()

@app.task(name='add_reward')
def add_reward():
    if CoinWallet.objects.count()>0:
        for wallet in CoinWallet.objects.all():
            wallet.add_reward_fee_in_second()

