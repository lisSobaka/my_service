# Generated by Django 4.2.4 on 2023-08-29 12:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_client_alter_order_date_creation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_creation',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 29, 12, 45, 50, 227400), null=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 29, 12, 45, 50, 228054)),
        ),
    ]
