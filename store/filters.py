from django_filters.rest_framework import FilterSet
from .models import Product

class productFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'id': ['exact'],
            'unit_price': ['gt', 'lt']
        }