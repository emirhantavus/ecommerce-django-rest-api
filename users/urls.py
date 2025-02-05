from django.urls import path
from .views import RegisterAPIView, LoginAPIView , ProtectedEndpoint

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path ('login/', LoginAPIView.as_view(),name='login'),
    path ('protected/',ProtectedEndpoint.as_view(),name='protected')
]