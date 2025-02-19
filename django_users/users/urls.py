from django.urls import path
from .views import (RegisterAPIView, LoginAPIView , ProtectedEndpoint , ProfileAPIView,
                    PasswordResetConfirmView , PasswordResetView,CheckTokenAPIView,)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path ('login/', LoginAPIView.as_view(),name='login'),
    path ('protected/',ProtectedEndpoint.as_view(),name='protected'),
    path('profile/<int:pk>/', ProfileAPIView.as_view(),name='profile'),
    path('password-reset/', PasswordResetView.as_view(),name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    
    ###########################
    ###########################
    path('check-token/', CheckTokenAPIView.as_view(),name='check-token'),
]