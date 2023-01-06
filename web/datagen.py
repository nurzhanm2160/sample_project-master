from django.utils import timezone
import string
import random
import decimal
import datetime

from coin.models import Coin, CoinWallet, CoinPrice, Deposit, Plan, RewardFee

from authentication.models import User

coins = [['Bitcoin', 'BTC'], ['Litecoin', 'LTC'], ['Ethereum', 'ETH'], ['Tron', 'TRX']]

def purge(modelname):
    if modelname.objects.count()>0:
        for i in modelname.objects.all():
            i.delete()

def run_purge():
    purge(Deposit)
    purge(CoinWallet)
    purge(CoinPrice)
    purge(Coin)
    purge(User)
    purge(Plan)
    purge(RewardFee)


def create_all_users():
    User.objects.create_superuser(email="admin@admin.com", password="q")

    for i in range(25):
        random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        User.objects.create_user(email=f"{random_string}@example.com", password="string")
        user = User.objects.filter(email=f"{random_string}@example.com")[0]
        if len(list(User.objects.all())) > 3:
            users_list = list(User.objects.all())
            users_list.remove(user)
            inviter = random.choice(users_list)
            user.recommended_by = inviter
            user.is_verified = True
            user.save()

def create_coins():
    for i in coins:
        Coin.objects.create(title=i[0], ticker=i[1])

def create_coin_prices():
    for i in range(10):
        for c in Coin.objects.all():
            c.get_newest_price()

def create_coin_wallet():
    for i in User.objects.all():
        for j in Coin.objects.all():
            CoinWallet.objects.create(owner=i, coin=j)

def update_coin_wallet():
    for i in CoinWallet.objects.all():
        all_vhs_power = i.owner.my_vhses
        i.vhs_power = all_vhs_power/4
        i.save()

def create_deposit():
    for i in range(10):
        for j in User.objects.all():
            new_date = timezone.now() - datetime.timedelta(days=i)
            amount = random.randint(0, 100)
            Deposit.objects.create(
                owner=j,
                deposit_amount_in_usd=amount,
                datetime_moment=new_date
            )

def create_plan():
    for i in range(6):
        Plan.objects.create(
            title=f"plan-{i}",
            percent_per_day=i
        )

def create_rewards():
    for wallet in CoinWallet.objects.all():
        for j in range(20):
            wallet.add_reward_fee_in_second()
            # print(f"{wallet} - {wallet.deposit_income}")

def run_datagen():
    create_all_users()
    create_coins()
    # create_coin_prices()
    create_coin_wallet()
    create_deposit()
    create_plan()
    update_coin_wallet()
    # create_rewards()

run_purge()
run_datagen()

# print('----------------------------')
# print(User.objects.last().my_wallets)
# print('----------------------------')
# print(User.objects.last().my_deposits)
# print('----------------------------')
# print(User.objects.last().my_vhses)
# print('----------------------------')
# print(User.objects.last().my_usd_investments_amount)
# print('----------------------------')
# print(User.objects.last().my_plan)
# print('----------------------------')
# print('*****************************')
# for c in Coin.objects.all():
#     c.get_newest_price()
# print('----------------------------')
# print('*****************************')
# for wallet in CoinWallet.objects.all():
#     print(f"{wallet} - {wallet.deposit_income}")
# print('----------------------------')
