# Generated by Django 3.2.16 on 2023-01-12 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('txid', models.CharField(max_length=255, null=True, verbose_name='txid')),
                ('private_hash', models.CharField(max_length=255, null=True, verbose_name='hash')),
                ('payment_id', models.CharField(default='0', max_length=255, null=True, unique=True, verbose_name='id платежа')),
                ('amount', models.IntegerField(blank=True, null=True, verbose_name='сумма')),
                ('amount_pay', models.IntegerField(blank=True, null=True, verbose_name='сумма платежа')),
                ('system', models.CharField(blank=True, max_length=255, null=True, verbose_name='Платежная система')),
                ('currency', models.CharField(blank=True, max_length=255, null=True, verbose_name='Валюта')),
                ('number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Кошелёк')),
                ('transaction_type', models.CharField(blank=True, max_length=255, null=True, verbose_name='Тип платежа')),
            ],
        ),
    ]
