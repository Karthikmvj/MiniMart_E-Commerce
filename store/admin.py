from django.contrib import admin
from .models import (Category, Product, ProductImage, Review, Cart, CartItem, Order, OrderItem, WishlistItem,
                     Brand, Color, OrderReturn, OrderCancellation, ReviewModeration, SavedSearch, Offer)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'original_price', 'stock', 'category', 'is_featured', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    readonly_fields = ('created_date', 'modified_date')
    inlines = [ProductImageInline]

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating', 'approved', 'created_at')
    list_filter = ('approved', 'rating')
    search_fields = ('name', 'comment', 'product__product_name')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'product_price', 'quantity')
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'first_name', 'last_name', 'phone', 'order_total', 'status', 'is_ordered', 'created_at')
    list_filter = ('status', 'is_ordered')
    search_fields = ('order_number', 'first_name', 'last_name', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(WishlistItem)

# New Admin Classes for New Models
class BrandAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'slug')
    prepopulated_fields = {'slug': ('brand_name',)}

class ColorAdmin(admin.ModelAdmin):
    list_display = ('color_name', 'color_code')

class OrderReturnAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason')
    search_fields = ('order__order_number', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

class OrderCancellationAdmin(admin.ModelAdmin):
    list_display = ('order', 'reason', 'refund_amount', 'is_approved', 'requested_at')
    list_filter = ('is_approved',)
    search_fields = ('order__order_number',)
    readonly_fields = ('requested_at',)

class ReviewModerationAdmin(admin.ModelAdmin):
    list_display = ('review', 'status', 'moderator', 'created_at')
    list_filter = ('status',)
    search_fields = ('review__product__product_name', 'review__name', 'moderator__username')
    readonly_fields = ('created_at',)

class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'category', 'created_at')
    search_fields = ('query', 'user__username')
    readonly_fields = ('created_at',)

admin.site.register(Brand, BrandAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(OrderReturn, OrderReturnAdmin)
admin.site.register(OrderCancellation, OrderCancellationAdmin)
admin.site.register(ReviewModeration, ReviewModerationAdmin)
admin.site.register(SavedSearch, SavedSearchAdmin)
admin.site.register(Offer)
