
from http.client import HTTPResponse
from django.shortcuts import render
from django.http import HttpResponse
from .models import Blockchain, SmartContract

def home(request):
    return render(request, 'cryptocurrencies/home.html')
def contracts(request):
    data = SmartContract.objects.all()
    return render(request, 'cryptocurrencies/contracts.html', {'data': data})