from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet , ProductAPIView , SellerProductsListView

router = DefaultRouter()
router.register(r'category',CategoryViewSet)

urlpatterns = [
      path('',ProductAPIView.as_view(),name='products'),
      path('seller/<int:seller_id>/products/',SellerProductsListView.as_view(),name='seller-products')
]

urlpatterns += router.urls