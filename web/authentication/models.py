import random
import string

from typing import TypeVar
from datetime import datetime

from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from rest_framework_simplejwt.tokens import RefreshToken

from .utils import generate_code
from .managers import UserManager
from coin.models import Coin, CoinPrice, CoinWallet, Deposit, Plan, RewardFee, Transaction


UserType = TypeVar('UserType', bound='User')


class User(AbstractUser, PermissionsMixin):

    username = None  # type: ignore
    email = models.EmailField(_('Email address'), unique=True, db_index=True)
    is_verified = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    referral_code = models.CharField(max_length=15, null=True, blank=True, unique=True)
    recommended_by = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name='referrals')
    some_data = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    sourse_name = models.CharField(max_length=255, null=True, blank=True)
    # transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True)

    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()  # type: ignore

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.email}"

    def save(self, *args, **kwargs):
        random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        self.referral_code = random_string
        if self.sourse_name:
            pass
        else:
            if self.recommended_by:
                self.sourse_name = self.recommended_by.sourse_name
            else:
                pass
        super(User, self).save(*args, **kwargs)

    @property
    def marketing_source(self):
        if self.sourse_name:
            marketing_source = self.sourse_name
        else:
            marketing_source = self.recommended_by.sourse_name
        return marketing_source

    @property
    def first_level_referrals(self):
        flr_guests = list(self.referrals.all())
        return flr_guests

    @property
    def second_level_referrals(self):
        slr_guests = []
        for i in self.first_level_referrals:
            for j in i.first_level_referrals:
                slr_guests.append(j)
        return slr_guests

    @property
    def my_referal_link(self):
        relativeLink = reverse('register')
        absurl = f"{relativeLink}?code={self.referral_code}"
        return absurl

    @property
    def my_wallets(self):
        wallets = []
        for wallet in self.wallets.all():
            wallets.append(wallet.wallet_info)
        return wallets

    @property
    def my_deposits(self):
        deposits = []
        for deposit in self.deposits.all():
            deposits.append(deposit)
        return deposits

    @property
    def my_usd_investments_amount(self):
        amount_in_usd = 0
        for deposit in self.my_deposits:
            amount_in_usd += deposit.deposit_amount_in_usd
        return amount_in_usd

    @property
    def my_vhses(self):
        amount_in_usd = 0
        for deposit in self.my_deposits:
            amount_in_usd += deposit.deposit_amount_in_usd
        vhses = amount_in_usd*40
        return vhses


    @property
    def my_plan(self):
        my_plan = ""
        transaction = Transaction.objects.filter(user_id=self.id, transaction_type='paid')
        my_investments = 0
        for my_investment in transaction:
            my_investments += my_investment.amount

        if my_investments == 0:
            my_plan = Plan.objects.filter(title__icontains="0").first()
        elif my_investments > 0 and my_investments<1000:
            my_plan = Plan.objects.filter(title__icontains="1").first()
        elif my_investments > 1000 and my_investments<10000:
            my_plan = Plan.objects.filter(title__icontains="2").first()
        elif my_investments > 20000 and my_investments<100000:
            my_plan = Plan.objects.filter(title__icontains="3").first()
        else:
            my_plan = Plan.objects.filter(title__icontains="4").first()
        return my_plan


    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
