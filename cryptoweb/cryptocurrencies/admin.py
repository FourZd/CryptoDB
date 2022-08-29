from django.contrib import admin
from .models import SmartContract, Blockchain

# Register your models here.

@admin.register(SmartContract)
class SmartContractAdmin(admin.ModelAdmin):
    list_display = ('address', 'blockchain', 'creator', 'block_number', 'creation_datetime')

@admin.register(Blockchain)
class BlockchainAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_of_contracts')