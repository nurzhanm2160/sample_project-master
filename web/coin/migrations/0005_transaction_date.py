# Generated by Django 3.2.16 on 2023-01-14 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coin', '0004_alter_transaction_payment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время создания транзакции'),
        ),
    ]