from unittest.util import _MAX_LENGTH
from django.db import models
from django.db.models import Count
from django.contrib import admin

class Blockchain(models.Model):
    name = models.CharField(max_length=20, verbose_name='Наименование')
    
    @property
    @admin.display(description='Количество контрактов сети',)
    def num_of_contracts(self):
        number = Blockchain.objects.values("contracts").filter(name=self.name)[0]
        return number.get('contracts', 'undefined')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Блокчейн'
        verbose_name_plural = 'Блокчейны'
        
class SmartContract(models.Model):
    address = models.CharField(max_length=42, verbose_name='Адрес')
    blockchain = models.ForeignKey(Blockchain, on_delete=models.PROTECT, related_name='contracts', default=None, verbose_name='Блокчейн')
    creator = models.CharField(blank=True, max_length=42, verbose_name='Создатель')
    block_number = models.IntegerField(default=None, verbose_name='Номер блока')
    creation_datetime = models.DateTimeField(blank=True, default=None, verbose_name='Дата и время создания')

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Смарт-контракт'
        verbose_name_plural = 'Смарт-контракты'
