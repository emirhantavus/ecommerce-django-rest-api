from django.urls import path
from .views import SellerDashboardView

urlpatterns = [
      path('seller/',SellerDashboardView.as_view(),name='seller-dashboard'),
]