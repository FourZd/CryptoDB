from django.db import models

class SmartContract(models.Model):
    address = models.CharField(max_length=200)
    blockchain = models.CharField(max_length=10)
    creator = models.CharField(blank=True, max_length=200)
    block_number = models.IntegerField()
    creation_datetime = models.DateTimeField(blank=True)


