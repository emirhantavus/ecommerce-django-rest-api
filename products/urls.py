from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet , deneme

router = DefaultRouter()
router.register(r'category',CategoryViewSet)

urlpatterns = [
      path('deneme/',deneme.as_view(),name='deneme')
]

urlpatterns += router.urls