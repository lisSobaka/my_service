# Generated by Django 4.1.7 on 2023-10-11 10:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_remove_payments_date_payments_date_creation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_creation',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='payments',
            name='date_creation',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата платежа'),
        ),
    ]
