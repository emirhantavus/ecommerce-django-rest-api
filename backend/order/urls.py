from django.urls import path
from .views import (OrderAPIView, UpdateOrderStatusAPIView, CancelOrderAPIView,
                    RequestReturnAPIView, ListReturnRequestsAPIView,ListReturnRequestsSellerAPIView,
                    ProcessReturnRequestsSellerAPIView)

urlpatterns = [
      path('',OrderAPIView.as_view(),name='order'),
      path('<int:o_id>/update-status/', UpdateOrderStatusAPIView.as_view(), name='update-order-status'),
      path('<int:o_id>/cancel/', CancelOrderAPIView.as_view(), name='cancel-order'),
      path('order-items/<int:item_id>/request-return/', RequestReturnAPIView.as_view(), name='request-return'),
      path('seller/return-requests/', ListReturnRequestsSellerAPIView.as_view(), name='seller-return-requests'),
      path('order-items/<int:item_id>/process-return/', ProcessReturnRequestsSellerAPIView.as_view(), name='process-return'),
      path('my/return-requests/', ListReturnRequestsAPIView.as_view(), name='my-return-requests')
]