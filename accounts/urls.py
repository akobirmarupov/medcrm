from __future__ import annotations

from django.urls import path
from accounts.routes.login_and_register.views import LoginAPIView, RegisterAPIView, VerifyOTPAPIView

app_name = "account"

urlpatterns = [
    # Auth
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),
   ]
