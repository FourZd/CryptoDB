
from http.client import HTTPResponse
from django.views.generic import ListView, TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from .models import Blockchain, SmartContract
from django.core import paginator

class ContractsPage(ListView):
    model = SmartContract
    template_name = 'cryptocurrencies/contracts.html'
    context_object_name = 'contracts'
    paginate_by = 20


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Smart Contracts'
        return context
    
    def get_queryset(self):
        return SmartContract.objects.select_related('blockchain').all()


class HomePage(TemplateView):
    template_name = 'cryptocurrencies/home.html'