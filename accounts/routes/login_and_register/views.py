from __future__ import annotations

from dataclasses import asdict

from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User

from accounts.routes.login_and_register.serializers import LoginSerializer, RegisterSerializer
from accounts.services import LoginService 
from common.throttles import LoginThrottle 
from accounts.email import send_otp_email, verify_otp_code


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]
    serializer_class = LoginSerializer

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tokens = LoginService().login(
                phone_number=serializer.validated_data["phone_number"],
                password=serializer.validated_data["password"],
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(asdict(tokens), status=status.HTTP_200_OK)
    


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data['email']

        cache.set(f'register_data_{email}',{
            "first_name": data["first_name"],
            "last_name":  data["last_name"],
            "email":      email,
            "phone_number": data["phone_number"],
            "password":   data["password"],
        }, timeout=60 * 5)
    
        ok = send_otp_email(email)

        if not ok:
            return Response(
                {"detail": "Email yuborishda xatolik yuz berdi. Keyinroq urinib ko'ring."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        
        return Response(
            {"detail": f"{email} manziliga tasdiqlash kodi yuborildi."},
            status=status.HTTP_200_OK,
        )
    

    
class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not verify_otp_code(email, code):
            return Response({'detail': "Kod muddati utgan yoki noto'gri kiritilgan."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        data = cache.get(f'register_data_{email}')
        if not data:
            return Response(
                {"detail": "Ma'lumot topilmadi. Qaytadan ro'yxatdan o'ting."},
                status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data['phone_number'],
            password=data['password'],
        )

        cache.delete(f'register_data_{email}')

        return Response(
            {"detail": "Ro'yxatdan muvaffaqiyatli o'tdingiz!"},
            status=status.HTTP_201_CREATED,
        )