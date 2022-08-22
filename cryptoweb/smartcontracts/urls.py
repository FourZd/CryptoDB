from django.urls import path

from . import views

urlpatterns = [
    path('table', views.contracts, name='table'),
]