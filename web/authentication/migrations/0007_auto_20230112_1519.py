# Generated by Django 3.2.16 on 2023-01-12 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coin', '0002_transaction'),
        ('authentication', '0006_user_sourse_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coin.transaction'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=True),
        ),
    ]
