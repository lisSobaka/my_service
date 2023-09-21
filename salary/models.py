from django.db import models
from users.models import Employees
from orders.models import Order, Works, Payments
from datetime import datetime


class Salary(models.Model):

    SALARY_REASONS = (
        ('BONUS', 'Премия'),
        ('PENALTY', 'Штраф'),
        ('ACCRUAL', 'Начисление за заказ'),
        ('PAYOUT', 'Выплата ЗП'),
        ('INTERIM_PAYMENT', 'Промежуточная выплата')
    )
    
    employee = models.ForeignKey(Employees, on_delete=models.DO_NOTHING, verbose_name='Исполнитель')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True,
                              verbose_name='Номер заказа')
    work = models.ForeignKey(Works, on_delete=models.CASCADE, null=True, blank=True,
                              verbose_name='Услуга')
    payment = models.ForeignKey(Payments, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='Платёж №')
    reason = models.CharField(max_length=30, verbose_name='Основание', choices=SALARY_REASONS,
                              default='ACCRUAL')
    date = models.DateTimeField(default=datetime.now())
    amount = models.IntegerField(verbose_name='Сумма')
    comment = models.CharField(max_length=100, blank=True, default='', verbose_name='Комментарий')
    paid_for_employee = models.BooleanField(default=False, verbose_name='Оплачено мастеру')
    paid_by_operation = models.IntegerField(blank=True, null=True, verbose_name='Закрыт операцией №')