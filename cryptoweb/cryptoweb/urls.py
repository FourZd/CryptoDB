
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('cryptocurrencies.urls', 'cryptocurrencies'), namespace='cryptocurrencies')),
    path('__debug__/', include('debug_toolbar.urls')),
]