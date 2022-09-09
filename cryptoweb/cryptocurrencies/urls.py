from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contracts/', views.contracts, name='cryptotable')
]