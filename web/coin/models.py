import json
import requests

from django.conf import settings
from django.db import models
from django.utils import timezone


class Coin(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    ticker = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.ticker

    @property
    def current_price(self):
        current_price = 0
        if len(list(self.prices.all())) > 0:
            current_price = list(self.prices.all())[-1].price_value
        return current_price

    @property
    def all_prices_dates(self):
        dates = []
        for price in self.prices.all():
            dates.append(price.price_date_time)
        return dates

    def get_newest_price(self):
        key = f"https://api.binance.com/api/v3/ticker/price?symbol={self.ticker}USDT"
        data = requests.get(key)
        data = data.json()
        CoinPrice.objects.create(coin=self, price_value=data['price'], price_date_time=timezone.now())
        # print(f"{data['symbol']} price is {data['price']}")

    class Meta:
        verbose_name = "Монета"
        verbose_name_plural = "Монеты"


class CoinPrice(models.Model):
    coin = models.ForeignKey(to=Coin, on_delete=models.SET_NULL, blank=True, null=True, related_name="prices")
    price_value = models.DecimalField(blank=True, null=True, max_digits=25, decimal_places=20)
    price_date_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Стоимость Монеты"
        verbose_name_plural = "Стоимость Монет"


class CoinWallet(models.Model):
    owner = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="wallets")
    coin = models.ForeignKey(to=Coin, on_delete=models.SET_NULL, blank=True, null=True, related_name="wallets")
    vhs_power = models.DecimalField(blank=True, null=True, max_digits=25, decimal_places=20, default=0)

    def __str__(self):
        return f"{self.owner.email} {self.coin}"

    def add_reward_fee_in_second(self):
        owner_plan = self.owner.my_plan
        fee_percent = owner_plan.percent_per_day
        usd_capital = self.vhs_power/40
        usd_reward_fee = usd_capital*fee_percent/100
        coin_current_price = self.coin.current_price
        if coin_current_price:
            crypto_reward_fee = usd_reward_fee/coin_current_price
            crypto_reward_fee_per_second = crypto_reward_fee/86400
            RewardFee.objects.create(coin_wallet=self, amount_in_coin=crypto_reward_fee_per_second)

    @property
    def deposit_income(self):
        income = 0
        all_rewards = self.fees.all()
        for reward in all_rewards:
            income += reward.amount_in_coin
        return income

    @property
    def wallet_info(self):
        info = {}
        info['owner'] = self.owner.email
        info['coin'] = self.coin.ticker
        info['vhs_power'] = self.vhs_power
        info['deposit_income'] = self.deposit_income
        return info

    class Meta:
        verbose_name = "Кошелек"
        verbose_name_plural = "Кошельки"


class Transaction(models.Model):
    # title = models.CharField(max_length=255, null=True, blank=True)
    # transaction = models.CharField('Транзакция', max_length=255, null=True, blank=False)
    txid = models.CharField('txid', max_length=255, null=True, blank=False)
    private_hash = models.CharField('hash', max_length=255, null=True, blank=False)
    payment_id = models.CharField('id платежа', max_length=255, null=True, blank=False, unique=True, default='0')
    amount = models.IntegerField('сумма', null=True, blank=True)
    amount_pay = models.IntegerField('сумма платежа', null=True, blank=True)
    system = models.CharField('Платежная система', max_length=255, null=True, blank=True)
    currency = models.CharField('Валюта', max_length=255, null=True, blank=True)
    number = models.CharField('Кошелёк', max_length=255, null=True, blank=True)
    transaction_type = models.CharField('Тип платежа', max_length=255, null=True, blank=True)

    # def __str__(self):
    #     return self.txid


class Deposit(models.Model):
    owner = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="deposits")
    deposit_amount_in_usd = models.DecimalField(blank=True, null=True, max_digits=25, decimal_places=20)
    datetime_moment = models.DateTimeField(blank=True, null=True)

    # @property
    # def crypto_amount(self):
    #     coin = self.coin_wallet.coin
    #     coin_prices = coin.all_prices_dates
    #     iskome_date = min(coin_prices, key=lambda sub: abs(sub - self.datetime_moment))
    #     coin_price = CoinPrice.objects.filter(coin=coin, price_date_time=iskome_date)[0].price_value
    #     crypto_amount = self.deposit_amount_in_usd/coin_price
    #     return crypto_amount

    # @property
    # def owner(self):
    #     return self.owner

    # @property
    # def coin(self):
    #     return self.coin_wallet.coin
    #

    class Meta:
        verbose_name = "Пополнение"
        verbose_name_plural = "Пополнения"


class Plan(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    percent_per_day = models.DecimalField(blank=True, null=True, max_digits=3, decimal_places=2)

    def __str__(self):
        return self.title


class RewardFee(models.Model):
    coin_wallet = models.ForeignKey(to=CoinWallet, on_delete=models.SET_NULL, blank=True, null=True, related_name="fees")
    amount_in_coin = models.DecimalField(blank=True, null=True, max_digits=25, decimal_places=20)

    class Meta:
        verbose_name = "Вознаграждение по депозиту"
        verbose_name_plural = "Вознаграждения по депозиту"
