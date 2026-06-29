from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import random
import string

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='userprofile/', blank=True)

    def __str__(self):
        return self.user.username


class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='Home')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.address_type} - {self.full_name}"


class PaymentMethod(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('UPI', 'UPI'),
        ('Wallet', 'Wallet'),
        ('GPay', 'GPay'),
        ('COD', 'Cash on Delivery'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    
    # For cards
    card_number = models.CharField(max_length=20, blank=True)
    card_holder_name = models.CharField(max_length=100, blank=True)
    expiry_date = models.CharField(max_length=7, blank=True)  # MM/YY format
    
    # For UPI
    upi_id = models.CharField(max_length=100, blank=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_type} - {self.user.username}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference')
    order_updates = models.BooleanField(default=True)
    promotional_emails = models.BooleanField(default=True)
    review_reminders = models.BooleanField(default=True)
    wishlist_updates = models.BooleanField(default=True)
    cart_reminders = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notifications for {self.user.username}"


# 2FA models removed
