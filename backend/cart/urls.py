from django.urls import path
from .views import CartItemCreateListAPIView, CartItemRetrieveOrDestroyAPIView, DeleteAllItemsAPIView

urlpatterns = [
      path('',CartItemCreateListAPIView.as_view(),name='cart-list-create'),
      path('<int:id>/',CartItemRetrieveOrDestroyAPIView.as_view(),name='cart-update-delete'),
      path('delete-all/',DeleteAllItemsAPIView.as_view(),name='cart-delete-all'),
]