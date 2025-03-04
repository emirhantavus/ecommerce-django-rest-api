from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
      CategoryViewSet , ProductAPIView , SellerProductsListView ,
      ProductUpdateDeleteAPIView , ProductDetailAPIView,)

router = DefaultRouter()
router.register(r'category',CategoryViewSet)

urlpatterns = [
      path('',ProductAPIView.as_view(),name='products'),
      path('<int:pk>/',ProductDetailAPIView.as_view(),name='product-detail'),
      path('seller/<int:seller_id>/products/',SellerProductsListView.as_view(),name='seller-products'),
      path('<int:pk>/update/',ProductUpdateDeleteAPIView.as_view(),name='product-update'),
      path('<int:pk>/delete/',ProductUpdateDeleteAPIView.as_view(),name='product-delete'),
]

urlpatterns += router.urls