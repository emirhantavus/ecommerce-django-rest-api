from django.urls import path
from .views import ReviewAPIView, UserReviewListAPIView, ReviewDetailAPIView

urlpatterns = [
      path("products/<int:product_id>/", ReviewAPIView.as_view(), name="product-review"),
      path("my-reviews/",UserReviewListAPIView.as_view(), name='my-reviews'),
      path("my-reviews/<int:pk>/", ReviewDetailAPIView.as_view(), name="review-detail"),
]