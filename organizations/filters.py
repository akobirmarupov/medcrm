import django_filters
from organizations.models import Clinic, Branch, Department, Room

class ClinicFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter()
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Clinic
        fields = ['is_active', 'name']


class BranchFilter(django_filters.FilterSet):
    clinic = django_filters.NumberFilter()        # ?clinic=1
    is_main = django_filters.BooleanFilter()      # ?is_main=true
    is_active = django_filters.BooleanFilter()    # ?is_active=true

    class Meta:
        model = Branch
        fields = ['clinic', 'is_main', 'is_active']


class DepartmentFilter(django_filters.FilterSet):
    branch = django_filters.NumberFilter()                  
    is_active = django_filters.BooleanFilter()                    
    name = django_filters.CharFilter(lookup_expr='icontains')    
    head_doctor = django_filters.NumberFilter()                  

    class Meta:
        model = Department
        fields = ['branch', 'is_active', 'name', 'head_doctor']


class RoomFilter(django_filters.FilterSet):
    department = django_filters.NumberFilter()                   
    room_type = django_filters.ChoiceFilter(choices=Room.RoomType.choices) 
    floor = django_filters.NumberFilter()                        
    is_active = django_filters.BooleanFilter()                      
    capacity_min = django_filters.NumberFilter(field_name='capacity', lookup_expr='gte') 
    capacity_max = django_filters.NumberFilter(field_name='capacity', lookup_expr='lte')  

    class Meta:
        model = Room
        fields = ['department', 'room_type', 'floor', 'is_active', 'capacity_min', 'capacity_max']