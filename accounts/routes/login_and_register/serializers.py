from __future__ import annotations

import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from accounts.models import User

_PHONE_RE = re.compile(r"^\+?\d{9,15}$")



class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate_phone_number(self, value: str) -> str:
        cleaned = value.replace(" ", "")
        if not _PHONE_RE.match(cleaned):
            raise serializers.ValidationError("Telefon raqam noto'g'ri formatda.")
        return cleaned
    

class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)



class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=120)
    last_name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=13)
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(write_only=True)


    def validate_phone_number(self, value):
        cleaned = value.replace(" ", "")
        if not _PHONE_RE.match(cleaned):
            raise serializers.ValidationError("Telefon raqam noto'g'ri formatda.")
        if User.objects.filter(phone_number=cleaned).exists():
            raise serializers.ValidationError("Bu telefon raqam band.")
        return cleaned

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email band.")
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password": "Parollar mos kelmadi."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
