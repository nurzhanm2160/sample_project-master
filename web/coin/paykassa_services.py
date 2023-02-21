from datetime import datetime, date

from django.db.models import Q
from django.shortcuts import get_object_or_404
from paykassa.dto import GetPaymentUrlRequest, GetPaymentUrlResponse, CheckPaymentRequest, CheckPaymentResponse, \
    GenerateAddressRequest, GenerateAddressResponse, MakePaymentRequest
from paykassa.merchant import MerchantApi
from paykassa.payment import PaymentApi
from paykassa.struct import CommissionPayer, Currency, TransactionPriority
from rest_framework.response import Response

from .check_payment_currency import check_payment_currency
from .check_payment_system import check_payment_system
from .models import Transaction, Coin, Deposit, CoinWallet, RewardFee, CoinPrice
from authentication.models import User


# from authentication.models import User

def _get_paykassa_client() -> MerchantApi:
    return MerchantApi(20854, "L4t12NTWJiHSiweped687VIL7iQ9MHpQ")


def _get_payment_url(amount: float, comment: str, system: str, currency: str, test: str) -> GetPaymentUrlResponse:
    """ Функция для получения ссылки для оплаты  """
    # varialbles from frontend
    get_payment_request = GetPaymentUrlRequest() \
        .set_amount(amount) \
        .set_currency(currency) \
        .set_system(system) \
        .set_comment(comment) \
        .set_paid_commission(CommissionPayer.CLIENT) \
        .set_test(test)

    return _get_paykassa_client().get_payment_url(get_payment_request)


def _get_transaction_by_order_id(order_id) -> str:
    """ Получаем транзакцию с помощью order_id """
    transaction = get_object_or_404(Transaction, payment_id=order_id)
    return transaction


def _change_transaction_status_to_paid(order_id):
    """ Меняем статус транзакции на оплачено и сохраняем в таблицу """
    transaction = _get_transaction_by_order_id(order_id)
    transaction.transaction_type = 'paid'
    transaction.save()


def _get_fresh_prices_and_calculate_currency_in_usd(currency: str, amount: float) -> int:
    """ Получаем текущую стоимость валюты и конвертируем её в USD """

    BTC = get_object_or_404(Coin, ticker='BTC')
    LTC = get_object_or_404(Coin, ticker='LTC')
    TRX = get_object_or_404(Coin, ticker='TRX')
    ETH = get_object_or_404(Coin, ticker='ETH')

    if currency == 'DOGE':
        return float(amount) * float(0.086)
    elif currency == 'BTC':
        return float(amount) * BTC.current_price
    elif currency == 'LTC':
        return float(amount) * LTC.current_price
    elif currency == 'TRX':
        return float(amount) * TRX.current_price
    elif currency == 'ETH':
        return float(amount) * ETH.current_price


def _get_user_by_id(user_id: int):
    return get_object_or_404(User, id=user_id)


def _create_user_deposit_and_save(user_id: int, amount_in_usd: float, term: int) -> None:
    """ Создаем депозит и сохраняем в него сумму в usd и пользователя, которому этот депозит принадлежит """
    user = _get_user_by_id(user_id)
    deposit = Deposit.objects.create(owner=user,
                                     deposit_amount_in_usd=amount_in_usd,
                                     datetime_moment=datetime.now(),
                                     term=term)
    deposit.save()


def _check_payment(order_id: int, test: str) -> CheckPaymentResponse:
    transaction = _get_transaction_by_order_id(order_id)

    check_payment_request = CheckPaymentRequest() \
        .set_private_hash(transaction.private_hash) \
        .set_test(test)

    return _get_paykassa_client().check_payment(check_payment_request)


def _generate_transaction_order_id() -> int:
    """ Функция для генерации order_id """
    transactions = Transaction.objects.filter(~Q(payment_id=0))
    return len(transactions) + 1


def _generate_address(amount: int, system: str, currency: str, user_id: int, comment: str, term: int) -> GenerateAddressResponse:

    client = _get_paykassa_client()
    user = _get_user_by_id(user_id)
    order_id = _generate_transaction_order_id()
    transaction = Transaction.objects.create(payment_id=order_id,
                                             amount=amount,
                                             system=system,
                                             currency=currency,
                                             term=term)
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

    return client.generate_address(generate_address_request)


def _save_private_hash_to_transaction(private_hash: str, order_id: int):
    """ Сохраняет приватный хэш в транзакции """
    transaction = get_object_or_404(Transaction, payment_id=order_id)
    transaction.private_hash = private_hash
    transaction.save()


def _get_currency_from_transaction(order_id: int):
    """ Получаем валюту из транзакции  """
    transaction = get_object_or_404(Transaction, payment_id=order_id)
    return transaction.currency


def _webhook(order_id: int, private_hash: str):
    """ Обрататывает данные, которые пришли от passkassa и создает депозит"""
    _change_transaction_status_to_paid(order_id=order_id)
    _save_private_hash_to_transaction(private_hash, order_id)

    transaction = _get_transaction_by_order_id(order_id)
    currency = transaction.currency
    amount = transaction.amount
    user_id = transaction.user_id
    term = transaction.term

    amount_in_usd = _get_fresh_prices_and_calculate_currency_in_usd(currency, amount)

    coin = Coin.objects.get(ticker='BTC')
    coin_wallet = CoinWallet(owner_id=user_id, vhs_power=10, coin=coin)
    coin_wallet.save()
    _create_user_deposit_and_save(user_id, amount_in_usd, term)


def _get_paykassa_payment_client():
    return PaymentApi(21855, "fqUUyP5ZX6JcCt798TjTsmFFqG8slXz7")


def _get_days_for_check_payment_amount(user_id: int):
    """ Получаем количество дней прошедших с момента депозита """
    deposit = get_object_or_404(Deposit, owner_id=user_id)
    days = datetime.now().date() - deposit.datetime_moment.date()
    return days


def _get_deposit_object(user_id: int):
    """ Возращает депозит пользователя с помощью user_id """
    return get_object_or_404(Deposit, owner_id=user_id)


def _get_user_reward(user_id: int, currency: str) -> float:
    """ Получаем сумму для вывода"""
    user_wallets = CoinWallet.objects.filter(owner__id=user_id)
    user_reward = 0

    for wallet in user_wallets:
        if wallet.wallet_info['coin'] == currency:
            user_reward += wallet.deposit_income

    return user_reward


def _clear_reward_after_withdraw(user_id: int, currency: str):
    """ Очищает reward, после вывода """
    user_wallets = CoinWallet.objects.filter(owner__id=user_id)
    for wallet in user_wallets:
        if wallet.wallet_info['coin'] == currency:
            wallet.deposit_income = 0


def _convert_usd_to_crypto(currency: str, amount_in_usd: float) -> float:
    """ Конвертирует USD в криптовалюту """
    coin = get_object_or_404(Coin, ticker=currency)
    coin_price = get_object_or_404(CoinPrice, coin=coin)
    return amount_in_usd / coin_price


def _clear_deposit(user_id: int, currency: str) -> float:
    """ очищает сумму депозита """
    deposit = _get_deposit_object(user_id)
    deposit_amount_in_usd = deposit.deposit_amount_in_usd
    deposit.deposit_amount_in_usd = 0
    deposit.save()
    return _convert_usd_to_crypto(currency, deposit_amount_in_usd)


def _cash_out(amount: float, system: str, currency: str, number: str):

    make_payment_request = MakePaymentRequest() \
    .set_shop("20268") \
    .set_amount(amount) \
    .set_priority(TransactionPriority.MEDIUM) \
    .set_system(system) \
    .set_currency(currency) \
    .set_paid_commission(CommissionPayer.SHOP) \
    .set_number(number) \
    .set_test("true") \

    return _get_paykassa_payment_client().make_payment(make_payment_request)


def _get_all_users():
    return User.objects.all()


def _get_all_deposits():
    transactions = Transaction.objects.filter(transaction_type='paid')
    deposit_sum = 0
    for transaction in transactions:
        deposit_sum += transaction.amount
    return deposit_sum


def _get_all_withdraws():
    transactions = Transaction.objects.filter(transaction_type='withdraw')
    withdraw_sum = 0
    for transaction in transactions:
        withdraw_sum += transaction.amount
    return withdraw_sum
