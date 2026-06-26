from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
# from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import User

from accounts.routes.forgot_password.serializers import (
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    PasswordResetConfirmSerializer,
)
from accounts.email import send_otp_email, verify_otp_code


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        ok = send_otp_email(email)
        if not ok:
            return Response({'detail': 'Email yuborishda xatolik yuz berdi!'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"detail": f'{email} manziliga tasdiqlash kodi yuborildi.'},
                        status=status.HTTP_200_OK)
    


class PasswordResetVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        if not verify_otp_code(email, code):
            return Response({"detail": "Kod notug'ri yoki muddati utgan."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # cache.set(f'password_reset_verified_{email}', True, timeout=60*10)

        user = User.objects.get(email=email)
        token = AccessToken.for_user(user)

        return Response({"detail": "Kod tasdiqlandi yangi parol o'rnating!",
                        "access": str(token)
                    }, status=status.HTTP_200_OK)
                    


class PasswordResetConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['new_password']

        request.user.set_password(new_password)
        request.user.save()

        return Response({"detail": "Parol muvaffaqiyatli yangilandi!"},
                        status=status.HTTP_200_OK)