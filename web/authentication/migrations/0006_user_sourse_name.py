# Generated by Django 3.2.15 on 2022-11-22 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_auto_20221009_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sourse_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
