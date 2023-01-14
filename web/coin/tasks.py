# Create your tasks here

from .models import Coin, CoinWallet, Transaction
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

@app.task(name='recalculate_amount')
def recalculate_amount(user_id):
    transaction = Transaction.objects.filter(user_id=user_id, transaction_type='paid')
    


