from __future__ import annotations

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView



def check_role(request: Request, allowed_roles: list[str]) -> bool:
    user = request.user
    return bool(user and user.is_authenticated and
                (getattr(user, 'role', None) in allowed_roles or user.is_superuser))



class IsAdmin(permissions.BasePermission):
    message = 'Bu amal faqat Admin uchun ruxsat etilgan!'

    def has_permissions(self, request: Request, view: APIView) -> bool:
        return check_role(request, ['ADMIN'])
    

class IsDoctor(permissions.BasePermission):
    message = 'Bu amal faqat Shifokor (Doctor) uchun ruxsat etilgan!'

    def has_permission(self, request: Request, view: APIView) -> bool:
        return check_role(request, ['DOCTOR'])
    

class IsNurse(permissions.BasePermission):
    message = 'Bu amal faqat Hamshira (Nurse) uchun ruxsat etilgan!'

    def has_permission(self, request: Request, view: APIView) -> bool:
        return check_role(request, ['NURSE'])
    

class IsReceptionist(permissions.BasePermission):
    message = 'Bu amal faqat Qabulxona xodimlari (Receptionist) uchun ruxsat etilgan!'

    def has_permission(self, request: Request, view: APIView) -> bool:
        return check_role(request, ['RECEPTIONIST'])
    

class IsPatient(permissions.BasePermission):
    message = 'Bu amal faqat Bemorlar uchun (Patient) uchun ruxsat etilgan!'

    def has_permission(self, request: Request, view: APIView) -> bool:
        return check_role(request, ['PATIENT'])
    

class IsAccountant(permissions.BasePermission):
    message = 'Bu amal faqat Bugalter (Accountant) uchun ruxsat etilgan!'

    def has_permission(self, request: Request, view: APIView) -> bool:
        return check_role(request, ['ACCOUNTANT'])
    




class IsMedicalStaff(permissions.BasePermission):
    """Tibbiy xodimlar uchun: Doctor, Nurse yoki Admin kirishi mumkin."""
    message = "Bu resurs faqat tibbiy xodimlar uchun."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return check_role(request, ["ADMIN", "DOCTOR", "NURSE"])


class IsOwnerOrMedicalStaff(permissions.BasePermission):
    """
    Obyekt darajasidagi tekshiruv:
    Obyekt egasi (Patient), shifokorlar, hamshiralar yoki admin ko'ra oladi.
    """
    message = "Bu ma'lumotni ko'rishga huquqingiz yo'q."

    def has_permission(self, request: Request, view: APIView) -> bool:
        # Avval foydalanuvchi tizimga kirganini tekshiramiz
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        user = request.user
        
        # Agar tibbiy xodim yoki admin bo'lsa, tekshirmasdan ruxsat beramiz
        if check_role(request, ["ADMIN", "DOCTOR", "NURSE", "RECEPTIONIST"]):
            return True
            
        # Agar bemor bo'lsa, faqat o'ziga tegishli obyektni ko'ra oladi
        owner_field = getattr(view, "owner_field", "user")
        owner = getattr(obj, owner_field, None)
        return owner == user