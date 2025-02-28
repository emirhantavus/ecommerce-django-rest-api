from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet , ProductAPIView

router = DefaultRouter()
router.register(r'category',CategoryViewSet)

urlpatterns = [
      path('products/',ProductAPIView.as_view(),name='products')
]

urlpatterns += router.urls