from django.urls import path
from .views import SellerDashboardView, AdminDashboardView

urlpatterns = [
      path('seller/',SellerDashboardView.as_view(),name='seller-dashboard'),
      path('admin/',AdminDashboardView.as_view(),name='admin-dashboard'),
]