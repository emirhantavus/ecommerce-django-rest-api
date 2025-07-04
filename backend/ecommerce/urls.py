from django.contrib import admin
from django.urls import path ,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/',include('users.urls')),
    path('api/products/',include('products.urls')),
    path('api/cart/',include('cart.urls')),
    path('api/order/',include('order.urls')),
    path('api/payment/',include('payment.urls')),
    path('silk/',include('silk.urls',namespace='silk')),
]