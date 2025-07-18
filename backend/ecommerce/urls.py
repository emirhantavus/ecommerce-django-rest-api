from django.contrib import admin
from django.urls import path ,include
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Ecommerce API",
        default_version='v1',
        description="API documentation for the Ecommerce Django project",
    ),
    public=True,
    permission_classes=[AllowAny],
    authentication_classes=[TokenAuthentication]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/',include('users.urls')),
    path('api/products/',include('products.urls')),
    path('api/cart/',include('cart.urls')),
    path('api/order/',include('order.urls')),
    path('api/payment/',include('payment.urls')),
    path('api/notifications/',include('notifications.urls')),
    path('silk/',include('silk.urls',namespace='silk')),
    ###
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]