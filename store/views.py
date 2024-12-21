from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .filters import productFilter
from .models import Product, Collection, OrderItem, Review
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer
from .pagination import DefaultPagination

# Create your views here.

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = productFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    def get_serializer_context(self):
        return {'request':self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).Count() > 0:
            return Response({'error':'Product can not be deleted because it is associated with an order item.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
            products_count=Count('products')).all()
    serializer_class = CollectionSerializer


    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=self.kwargs['pk'])
        if collection.products.count() > 0:
            return Response({'error':'Collection can not be deleted because it includes one or more products'},
                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
   
   
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}