from django.db import models
from django.urls import reverse


class ClientSource(models.Model):
    source = models.CharField(max_length=30, default='', blank=True)

    def __str__(self):
        return self.source


class Client(models.Model):
    name = models.CharField(max_length=40, verbose_name='Имя')
    tel = models.CharField(max_length=15, verbose_name='Номер телефона')
    email = models.EmailField(blank=True, default='', verbose_name='E-mail')
    source = models.ForeignKey(ClientSource, on_delete=models.PROTECT, 
                               null=True, blank=True, verbose_name='Источник')
    adress = models.CharField(max_length=150, blank=True, default='', verbose_name='Адрес')
    comment_client = models.CharField(max_length=50, blank=True, default='', 
                                      verbose_name='Комментарий о клиенте')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('clients', kwargs={'client_id': self.pk})