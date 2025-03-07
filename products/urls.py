from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
      CategoryViewSet , ProductAPIView , SellerProductsListView ,
      ProductUpdateDeleteAPIView , ProductDetailAPIView, FavoritesAPIView)

router = DefaultRouter()
router.register(r'category',CategoryViewSet)

urlpatterns = [
      path('',ProductAPIView.as_view(),name='products'),
      path('<int:pk>/',ProductDetailAPIView.as_view(),name='product-detail'),
      path('seller/<int:seller_id>/products/',SellerProductsListView.as_view(),name='seller-products'),
      path('<int:pk>/update/',ProductUpdateDeleteAPIView.as_view(),name='product-update'),
      path('<int:pk>/delete/',ProductUpdateDeleteAPIView.as_view(),name='product-delete'),
      path('favorites/',FavoritesAPIView().as_view(),name='favorites'),
      path('favorite/<int:favorite_id>/',FavoritesAPIView().as_view(),name='favorite-delete'),
]

urlpatterns += router.urls