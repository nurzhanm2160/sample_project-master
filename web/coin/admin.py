from django.contrib import admin
from .models import Coin, CoinPrice, CoinWallet, Transaction, Deposit, RewardFee
# Register your models here.

# admin.site.unregister(Coin)
# admin.site.unregister(Deposit)
# admin.site.unregister(CoinPrice)
# admin.site.unregister(CoinWallet)

class CoinAdmin(admin.ModelAdmin):
    list_display = ('title', 'ticker', 'current_price')

class CoinWalletAdmin(admin.ModelAdmin):
    list_display = ('owner', 'coin', 'vhs_power')

class CoinPriceAdmin(admin.ModelAdmin):
    list_display = ('coin', 'price_value', 'price_date_time')

class DepositAdmin(admin.ModelAdmin):
    list_display = ('owner', 'deposit_amount_in_usd', 'datetime_moment')

class RewardFeeAdmin(admin.ModelAdmin):
    list_display = ('coin_wallet', 'amount_in_coin')


admin.site.register(Coin, CoinAdmin)
admin.site.register(CoinPrice, CoinPriceAdmin)
admin.site.register(CoinWallet, CoinWalletAdmin)
admin.site.register(RewardFee, RewardFeeAdmin)
