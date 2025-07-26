from django.urls import path
from .views import ReviewAPIView

urlpatterns = [
      path("products/<int:product_id>/", ReviewAPIView.as_view(), name="product-review"), 
]