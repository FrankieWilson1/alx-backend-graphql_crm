import django_filters
from django_filters import rest_framework as filters
from .models import Customer, Product, Order


class CustomerFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    
    phone_pattern = filters.CharFilter(method='filter_by_phone_pattern')

    class Meta:
        model = Customer
        fields = ['name', 'email']

    def filter_by_phone_pattern(self, queryset, name, value):
        return queryset.filter(phone__startswith=value)


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    price = filters.RangeFilter()
    stock = filters.RangeFilter()
    low_stock = filters.NumberFilter(field_name='stock', lookup_expr='lt')

    class Meta:
        model = Product
        fields = ['name']


class OrderFilter(filters.FilterSet):
    customer_name = filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = filters.CharFilter(field_name='product__name', lookup_expr='icontains')
    product_id = filters.CharFilter(method='filter_by_product_id')

    class Meta:
        model = Order
        fields = ['total_amount', 'order_date']

    def filter_by_product_id(self, queryset, name, value):
        return queryset.filter(product__id=value)
