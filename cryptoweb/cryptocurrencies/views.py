
from http.client import HTTPResponse
from django.shortcuts import render
from django.http import HttpResponse

def main_page(request):
    return HttpResponse('<h1> You are at the main page </h1>')
def contracts(request):
    return HttpResponse('Testing')