from django.urls import path
from .views import OrderAPIView, UpdateOrderStatusAPIView, CancelOrderAPIView

urlpatterns = [
      path('',OrderAPIView.as_view(),name='order'),
      path('/<int:order_id>/update-status/', UpdateOrderStatusAPIView.as_view(), name='update-order-status'),
      path('/<int:order_id>/cancel/', CancelOrderAPIView.as_view(), name='cancel-order'),
]