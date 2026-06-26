from __future__ import annotations

from django.urls import path
from accounts.routes.login_and_register.views import LoginAPIView, RegisterAPIView, VerifyOTPAPIView
from accounts.routes.forgot_password.views import PasswordResetRequestView, PasswordResetConfirmView, PasswordResetVerifyView


app_name = "account"

urlpatterns = [
    # Auth
    path("auth/login/", LoginAPIView.as_view()),
    path("auth/register/", RegisterAPIView.as_view()),
    path('verify-otp/', VerifyOTPAPIView.as_view()),

    #forgot_password
    path('forgot-password/', PasswordResetRequestView.as_view()),
    path('forgot-password/verify/', PasswordResetVerifyView.as_view()),
    path('forgot-password/confirm/', PasswordResetConfirmView.as_view()),
   ]
