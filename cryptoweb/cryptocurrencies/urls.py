from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('contracts/', ContractsPage.as_view(), name='cryptotable')
]