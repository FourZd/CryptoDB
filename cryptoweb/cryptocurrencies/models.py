from unittest.util import _MAX_LENGTH
from django.db import models
from django.db.models import Count

class Blockchain(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Блокчейн'
        verbose_name_plural = 'Блокчейны'
        
class SmartContract(models.Model):
    address = models.CharField(max_length=200)
    blockchain = models.ForeignKey(Blockchain, on_delete=models.PROTECT, related_name='contracts', default=None)
    creator = models.CharField(blank=True, max_length=200)
    block_number = models.IntegerField(default=None)
    creation_datetime = models.DateTimeField(blank=True, default=None)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Смарт-контракт'
        verbose_name_plural = 'Смарт-контракты'
