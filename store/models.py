from django.db import models
from django.urls import reverse
from django.db.models import Avg
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    category_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    @property
    def translated_name(self):
        from django.utils import translation
        if translation.get_language() == 'ta':
            from .translations import TAMIL_TRANSLATIONS
            return TAMIL_TRANSLATIONS.get(self.category_name, self.category_name)
        return self.category_name

    @property
    def translated_description(self):
        from django.utils import translation
        if translation.get_language() == 'ta':
            from .translations import TAMIL_TRANSLATIONS
            return TAMIL_TRANSLATIONS.get(self.description, self.description)
        return self.description

    def __str__(self):
        return self.category_name


class Brand(models.Model):
    brand_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    @property
    def translated_name(self):
        from django.utils import translation
        if translation.get_language() == 'ta':
            from .translations import TAMIL_TRANSLATIONS
            return TAMIL_TRANSLATIONS.get(self.brand_name, self.brand_name)
        return self.brand_name

    @property
    def translated_description(self):
        from django.utils import translation
        if translation.get_language() == 'ta':
            from .translations import TAMIL_TRANSLATIONS
            return TAMIL_TRANSLATIONS.get(self.description, self.description)
        return self.description

    def __str__(self):
        return self.translated_name


class Color(models.Model):
    color_name = models.CharField(max_length=50, unique=True)
    color_code = models.CharField(max_length=7, default='#000000', help_text='Hex color code')

    def __str__(self):
        return self.color_name

    @property
    def translated_name(self):
        from django.utils import translation
        if translation.get_language() == 'ta':
            from .translations import TAMIL_TRANSLATIONS
            return TAMIL_TRANSLATIONS.get(self.color_name, self.color_name)
        return self.color_name


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text='Mark as featured product')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    colors = models.ManyToManyField(Color, blank=True)
    offer = models.ForeignKey('Offer', on_delete=models.SET_NULL, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def save(self, *args, **kwargs):
        if self.offer:
            today = timezone.now().date()
            if self.offer.active and self.offer.start_date <= today and self.offer.end_date >= today:
                if not self.original_price:
                    self.original_price = self.price
                discount = (self.original_price * self.offer.discount_percentage) / 100
                self.price = self.original_price - discount
            else:
                if self.original_price:
                    self.price = self.original_price
        else:
            if self.original_price:
                self.price = self.original_price

        super().save(*args, **kwargs)

    @property
    def review_count(self):
        return self.reviews.filter(approved=True).count()

    @property
    def average_rating(self):
        average = self.reviews.filter(approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(average, 1) if average else None

    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def translated_name(self):
        from django.utils import translation
        if translation.get_language() == 'ta':
            from .translations import TAMIL_TRANSLATIONS
            return TAMIL_TRANSLATIONS.get(self.product_name, self.product_name)
        return self.product_name

    @property
    def translated_description(self):
        from django.utils import translation
        if translation.get_language() == 'ta':
            from .translations import TAMIL_TRANSLATIONS
            return TAMIL_TRANSLATIONS.get(self.description, self.description)
        return self.description

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='photos/products')
    caption = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.product.product_name} image"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=80)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    image = models.ImageField(upload_to='photos/reviews/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.product.product_name} by {self.name}"

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.product_name

class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Return_Requested', 'Return Requested'),
        ('Returned', 'Returned'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    can_return_until = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.can_return_until:
            base_time = self.created_at or timezone.now()
            self.can_return_until = base_time + timedelta(days=7)
        super().save(*args, **kwargs)

    def can_be_returned(self):
        return self.status == 'Delivered' and timezone.now() < self.can_return_until

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def sub_total(self):
        return self.product_price * self.quantity

    def __str__(self):
        return self.product.product_name

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.product_name}"


class OrderReturn(models.Model):
    RETURN_REASON_CHOICES = (
        ('Defective', 'Defective Product'),
        ('Wrong_Item', 'Wrong Item Received'),
        ('Not_As_Described', 'Not As Described'),
        ('Changed_Mind', 'Changed Mind'),
        ('Other', 'Other'),
    )
    RETURN_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Refunded', 'Refunded'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=RETURN_REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='Pending')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return for Order {self.order.order_number}"


class OrderCancellation(models.Model):
    CANCEL_REASON_CHOICES = (
        ('Wrong_Item', 'Wrong Item'),
        ('Not_Needed', 'Not Needed Anymore'),
        ('Found_Better_Price', 'Found Better Price'),
        ('Other', 'Other'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='cancellation')
    reason = models.CharField(max_length=50, choices=CANCEL_REASON_CHOICES)
    description = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Cancellation for {self.order.order_number}"


class ReviewModeration(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='moderation')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reviews')
    reason_for_rejection = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Moderation: {self.review}"


class SavedSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    query = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.query}"

class Offer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
