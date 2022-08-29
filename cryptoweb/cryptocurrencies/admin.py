from django.contrib import admin
from .models import SmartContract, Blockchain

# Register your models here.

@admin.register(SmartContract, Blockchain)
class CryptoCurrenciesAdmin(admin.ModelAdmin):
    pass

 