
from http.client import HTTPResponse
from django.shortcuts import render
from django.http import HttpResponse
from .models import Blockchain, SmartContract

def main_page(request):
    return HttpResponse('<h1> You are at the main page </h1>')
def contracts(request):
    data = SmartContract.objects.all()
    return render(request, 'cryptocurrencies/contracts.html', {'data': data})