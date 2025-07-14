from django.urls import path
from .views import PaymentAPIView , SellerSalesListAPIView, PaymentListCustomerAPIView
urlpatterns = [
      path('',PaymentAPIView.as_view(),name='payment'),
      path('my/', PaymentListCustomerAPIView.as_view(), name='payment-list-customer'),
      path('seller/sales/', SellerSalesListAPIView.as_view(), name='seller-sales-list'),
]