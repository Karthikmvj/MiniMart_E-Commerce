from django.contrib import admin
from .models import (UserProfile, Address, PaymentMethod, NotificationPreference)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'address_type', 'is_default', 'city', 'country')
    list_filter = ('address_type', 'is_default', 'country')
    search_fields = ('user__username', 'full_name', 'city')

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_type', 'card_holder_name', 'is_default', 'is_active')
    list_filter = ('payment_type', 'is_default', 'is_active')
    search_fields = ('user__username', 'card_holder_name')

class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_updates', 'promotional_emails', 'sms_notifications')
    search_fields = ('user__username',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(NotificationPreference, NotificationPreferenceAdmin)