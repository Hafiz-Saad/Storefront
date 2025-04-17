from django.contrib import admin, messages
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from . import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['subcollection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    list_display = ['title', 'unit_price',
                    'inventory_status', 'subcollection_title', 'collection_title']
    list_editable = ['unit_price']
    list_filter = ['subcollection', 'last_update']
    list_per_page = 10
    list_select_related = ['subcollection', 'subcollection__collection']
    search_fields = ['title']

    def collection_title(self, product):
        return product.subcollection.collection.title
    
    def subcollection_title(self, product):
        return product.subcollection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.',
            messages.ERROR
        )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['featured_product']
    list_display = ['title', 'subcollections_count', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='subcollections_count')
    def subcollections_count(self, collection):
        url = (
            reverse('admin:store_subcollection_changelist')
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            }))
        return format_html('<a href="{}">{} Subcollections</a>', url, collection.subcollections_count)

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'subcollection__collection__id': str(collection.id)
            }))
        return format_html('<a href="{}">{} Products</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            subcollections_count=Count('subcollections'),
            products_count=Count('subcollections__products', distinct=True)
        )


@admin.register(models.SubCollection)
class SubCollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection', 'featured_product']
    list_display = ['title', 'collection_title', 'products_count']
    list_filter = ['collection']
    list_select_related = ['collection']
    search_fields = ['title', 'collection__title']

    def collection_title(self, subcollection):
        return subcollection.collection.title

    @admin.display(ordering='products_count')
    def products_count(self, subcollection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'subcollection__id': str(subcollection.id)
            }))
        return format_html('<a href="{}">{} Products</a>', url, subcollection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )


# Register the remaining models as they were before
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']