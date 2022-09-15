from django import template

from cryptocurrencies.models import SmartContract

register = template.Library()

@register.simple_tag
def get_contracts_data():
    return SmartContract.objects.all()