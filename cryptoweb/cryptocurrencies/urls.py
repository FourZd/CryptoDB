from django.urls import path

from . import views

urlpatterns = [
    path('', views.main_page, name='Main page'),
    path('contracts/', views.contracts, name='Contracts')
]