# Generated by Django 4.2.4 on 2023-09-01 10:41

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0005_alter_order_date_creation_alter_orderhistory_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='repairer',
        ),
        migrations.RemoveField(
            model_name='orderhistory',
            name='repairer',
        ),
        migrations.RemoveField(
            model_name='works',
            name='repairer',
        ),
        migrations.AddField(
            model_name='order',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель'),
        ),
        migrations.AddField(
            model_name='orderhistory',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель'),
        ),
        migrations.AddField(
            model_name='payments',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель'),
        ),
        migrations.AddField(
            model_name='works',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель'),
        ),
        migrations.AlterField(
            model_name='order',
            name='date_creation',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 1, 10, 41, 53, 706926), null=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 1, 10, 41, 53, 707619)),
        ),
        migrations.AlterField(
            model_name='payments',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 1, 10, 41, 53, 707989), verbose_name='Дата платежа'),
        ),
    ]
