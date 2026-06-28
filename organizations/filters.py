import django_filters
from organizations.models import Clinic, Branch

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