from django.db import models
from django.urls import reverse
from datetime import datetime
from django.core.cache import cache
from clients.models import Client
from users.models import Employees


class Order(models.Model):    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-pk']

    def get_absolute_url(self):
        return reverse('order', kwargs={'order_id': self.pk})
    
    def get_finance_data(self):
        works = Works.objects.filter(order_id=self.pk)
        payments = Payments.objects.filter(order_id=self.pk)
        prepayments_sum, profit, price = 0, 0, 0
        # Расчёт суммы предоплаты в заказе (предоплаты - возврат предоплат)
        for payment in payments:
            prepayments_sum += payment.income + payment.expense
        # Расчёт общей стоимости чистой прибыли заказа
        for work in works:
            work_price = (work.price - work.discount) * work.quantity
            price += work_price
            profit += work_price - (work.cost * work.quantity)
        # Расчёт оставшейся суммы оплаты для клиента
        client_debt = price - prepayments_sum
        finance_data = {'profit': profit, 'client_debt': client_debt}
        return finance_data
    

    def get_order_data(self):
        order_data = {}
        order_data['order'] = self
        order_data['client'] = order_data['order'].client
        order_data['works'] = Works.objects.filter(order_id=order_data['order'].pk)
        order_data['payments'] = Payments.objects.filter(order_id=order_data['order'].pk)
        order_data['history'] = OrderHistory.objects.filter(order_id=order_data['order'].pk).order_by('-pk')
        print('!!!!! ДАННЫЕ ИЗ БД !!!!!')
        cache.set_many({
            'order': order_data['order'],
            'client': order_data['client'],
            'works': order_data['works'],
            'payments': order_data['payments'],
            'history': order_data['history']
        })
        return order_data

    def get_order_data_cached(self):
        order_data_cached = {}
        order_data_cached['order'] = cache.get('order')
        order_data_cached['client'] = cache.get('client')
        order_data_cached['works'] = cache.get('works')
        order_data_cached['payments'] = cache.get('payments')
        order_data_cached['history'] = cache.get('history')
        print('!!!!! ДАННЫЕ ИЗ КЭША !!!!!')
        if not order_data_cached['order']:
            order_data_cached = self.get_order_data()
        return order_data_cached

    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name='Клиент')
    employee = models.ForeignKey(Employees, on_delete=models.PROTECT, null=True, blank=True, 
                                verbose_name='Исполнитель')
    whats_broken = models.CharField(max_length=50, verbose_name='Неисправность')
    device_appearance = models.CharField(max_length=80, blank=True, 
                                         default='', verbose_name='Состояние')
    device_type = models.CharField(max_length=20, blank=True, default='', 
                                   verbose_name='Тип устройства')
    imei = models.CharField(max_length=20, blank=True, default='', verbose_name='IMEI/SN')
    device_brand = models.CharField(max_length=20, verbose_name='Производитель')
    device_model = models.CharField(max_length=20, verbose_name='Модель')
    device_kit = models.CharField(max_length=80, blank=True, default='', 
                                  verbose_name='Комплектация')
    device_pass = models.CharField(max_length=20, blank=True, default='', 
                                   verbose_name='Пароль')
    price = models.IntegerField(verbose_name='Орентировоная стоимость')
    note_hidden = models.CharField(max_length=150, blank=True, default='',
                                   verbose_name='Заметки клиент НЕ видит')
    note_client = models.CharField(max_length=150, blank=True, default='', 
                                   verbose_name='Заметки клиент видит')
    prepayment = models.IntegerField(null=True, blank=True, default=0, 
                                     verbose_name='Предоплата')
    profit = models.IntegerField(null=True, default=0, verbose_name='Профит')
    debt = models.IntegerField(null=True, default=0, verbose_name='Клиент должен')
    date_creation = models.DateTimeField(default=datetime.now(), null=True, verbose_name='Дата создания')
    date_completion = models.DateTimeField(null=True, verbose_name='Дата готовности')
    in_work = models.BooleanField(default=True)


class Payments(models.Model):
    PAYMENT_REASONS = (
        ('PREPAYMENT', 'Предоплата'),
        ('ORDER_PAYMENT', 'Оплата заказа'),
        ('REFUND', 'Возврат предоплаты'),
        ('SALARY_PAYOUT', 'Выплата заработной платы'),
    )

    # def get_absolute_url(self):
    #     return reverse('payments/', kwargs={'pk': self.pk})
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, 
                                verbose_name='Заказ')
    employee = models.ForeignKey(Employees, on_delete=models.PROTECT, null=True, blank=True, 
                                verbose_name='Исполнитель')
    payment_reason = models.CharField(max_length=30, verbose_name='Тип платежа',
                                    choices=PAYMENT_REASONS)
    date = models.DateTimeField(default=datetime.now(), verbose_name='Дата платежа')
    income = models.IntegerField(null=True, default=0, verbose_name='Приход')
    expense = models.IntegerField(null=True, default=0, verbose_name='Расход')
    comment = models.CharField(max_length=30, verbose_name='Комментарий', blank=True, default='')


class Works(models.Model):

    def get_absolute_url(self):
        return reverse('edit_work', kwargs={'order_id': self.order_id, 'work_id': self.pk})

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    employee = models.ForeignKey(Employees, on_delete=models.PROTECT, null=True, blank=True, 
                                verbose_name='Исполнитель')
    payment = models.ForeignKey(Payments, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='Платёж №')
    work = models.CharField(max_length=50, verbose_name='Название услуги')
    price = models.IntegerField(verbose_name='Стоимость')
    cost = models.IntegerField(default=0, blank=True, verbose_name='Себестоимость')
    guarantee = models.IntegerField(default=60, verbose_name='Гарантия')
    discount = models.IntegerField(default=0, blank=True, verbose_name='Скидка')
    quantity = models.IntegerField(default=1, verbose_name='Количество')
    paid_by_client = models.BooleanField(default=False, verbose_name='Оплачено клиентом')


class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    employee = models.ForeignKey(Employees, on_delete=models.PROTECT, null=True, blank=True, 
                                verbose_name='Исполнитель')
    date = models.DateTimeField(default=datetime.now())
    message = models.CharField(max_length=200, verbose_name='Сообщение')