# Generated by Django 4.1.7 on 2023-09-18 15:26

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0008_alter_order_date_creation_alter_orderhistory_date_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('BONUS', 'Премия'), ('PENALTY', 'Штраф'), ('ACCRUAL', 'Начисление за заказ'), ('PAYOUT', 'Выплата ЗП'), ('INTERIM_PAYMENT', 'Промежуточная выплата')], default='ACCRUAL', max_length=30, verbose_name='Основание')),
                ('date', models.DateTimeField(default=datetime.datetime(2023, 9, 18, 19, 26, 14, 865019))),
                ('amount', models.IntegerField(verbose_name='Сумма')),
                ('comment', models.CharField(blank=True, default='', max_length=100, verbose_name='Комментарий')),
                ('paid_for_employee', models.BooleanField(default=False, verbose_name='Оплачено мастеру')),
                ('paid_by_operation', models.IntegerField(blank=True, null=True, verbose_name='Закрыт операцией №')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.order', verbose_name='Номер заказа')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.payments', verbose_name='Платёж №')),
                ('work', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.works', verbose_name='Услуга')),
            ],
        ),
    ]
