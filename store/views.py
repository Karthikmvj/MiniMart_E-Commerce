from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q, Avg, F, Count
from django.core.paginator import Paginator

# Importing forms defined in your forms.py
from .forms import (
    ProductForm, ReviewForm, CSVUploadForm, ProductFilterForm,
    OrderReturnForm, OrderCancellationForm, SavedSearchForm
)

from .models import Product, Review, OrderReturn, OrderCancellation, SavedSearch, Order, Category, ReviewModeration, WishlistItem, Cart, CartItem, OrderItem
import datetime
# ---------------------------------------------------------
# Main & Static Pages
# ---------------------------------------------------------
def home(request):
    categories = Category.objects.all()
    
    # Helper for common annotations to prevent N+1 queries
    def annotate_products(qs):
        return qs.annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__approved=True)),
            num_reviews=Count('reviews', filter=Q(reviews__approved=True))
        )

    # Product Slider: Fetching the 8 newest products
    recent_products = annotate_products(Product.objects.filter(is_available=True).select_related('category', 'brand').prefetch_related('colors').order_by('-created_date')[:8])
    # Featured Products: Limiting to 8 items to preserve layout and optimizing DB query
    featured_products = annotate_products(Product.objects.filter(is_featured=True, is_available=True).select_related('category', 'brand').prefetch_related('colors')[:8])
    # Best Offers
    best_offers = annotate_products(Product.objects.filter(is_available=True).select_related('category', 'brand').prefetch_related('colors').order_by('price')[:6])
    # Deals of the Day
    deals_of_the_day = annotate_products(Product.objects.filter(is_available=True).select_related('category', 'brand').prefetch_related('colors').order_by('?')[:6])
    
    # Trending Products: Chunked into sets of 4 for the carousel
    trending_qs = annotate_products(Product.objects.filter(is_available=True).select_related('category', 'brand').prefetch_related('colors')).order_by(F('avg_rating').desc(nulls_last=True))[:12]
    trending_products = [trending_qs[i:i + 4] for i in range(0, len(trending_qs), 4)]
    
    context = {
        'categories': categories,
        'recent_products': recent_products,
        'featured_products': featured_products,
        'best_offers': best_offers,
        'deals_of_the_day': deals_of_the_day,
        'trending_products': trending_products,
    }
    return render(request, 'store/home.html', context)

def about_us(request):
    return render(request, 'store/about_us.html')

def contact_us(request):
    return render(request, 'store/contact_us.html')

def privacy_policy(request):
    return render(request, 'store/privacy_policy.html')

def terms_conditions(request):
    return render(request, 'store/terms_conditions.html')

# ---------------------------------------------------------
# Products & Categories
# ---------------------------------------------------------
def product_list(request, category_slug=None):
    products = Product.objects.filter(is_available=True).select_related('category', 'brand').prefetch_related('colors')
    
    # General Keyword Search
    keyword = request.GET.get('keyword')
    if keyword:
        products = products.filter(
            Q(product_name__icontains=keyword) | 
            Q(description__icontains=keyword) |
            Q(category__category_name__icontains=keyword) |
            Q(brand__brand_name__icontains=keyword) |
            Q(colors__color_name__icontains=keyword)
        ).distinct()

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        
    # Annotate Average Rating to support rating filters and sorting
    products = products.annotate(avg_rating=Avg('reviews__rating', filter=Q(reviews__approved=True)))

    query_data = request.GET.copy()
    if category_slug and not query_data.getlist('category'):
        query_data.setlist('category', [str(category.id)])
    form = ProductFilterForm(query_data or None)
    if form.is_valid():
        categories = form.cleaned_data.get('category')
        brands = form.cleaned_data.get('brand')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        rating = form.cleaned_data.get('rating')
        sort_by = form.cleaned_data.get('sort')

        if categories:
            products = products.filter(category__in=categories)
        if brands:
            products = products.filter(brand__in=brands)
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        if rating:
            products = products.filter(avg_rating__gte=float(rating))
            
        if sort_by == 'newest':
            products = products.order_by('-created_date')
        elif sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'rating':
            products = products.order_by(F('avg_rating').desc(nulls_last=True))
            
    # Pagination
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    paged_products = paginator.get_page(page_number)
    query_params = request.GET.copy()
    query_params.pop('page', None)
    
    context = {
        'products': paged_products,
        'product_count': products.count(),
        'category': category,
        'form': form,
        'keyword': keyword,
        'query_string': query_params.urlencode(),
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, category_slug, product_slug):
    product = get_object_or_404(Product.objects.select_related('category', 'brand').prefetch_related('extra_images', 'colors'), category__slug=category_slug, slug=product_slug)
    reviews = product.reviews.filter(approved=True)
    review_form = ReviewForm()
    user_review = None
    in_wishlist = False
    wishlist_product_ids = []
    can_review = False
    
    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, product=product).first()
        if user_review:
            review_form = ReviewForm(instance=user_review)
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()
        wishlist_product_ids = list(WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True))
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__is_ordered=True,
            order__status='Delivered'
        ).exists()
    
    related_products = Product.objects.filter(category=product.category, is_available=True).select_related('category', 'brand').prefetch_related('colors').exclude(id=product.id)[:4]
    featured_products = Product.objects.filter(is_featured=True, is_available=True).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': review_form,
        'related_products': related_products,
        'featured_products': featured_products,
        'in_wishlist': in_wishlist,
        'wishlist_product_ids': wishlist_product_ids,
        'can_review': can_review,
    }
    return render(request, 'store/product_detail.html', context)

@user_passes_test(lambda u: u.is_staff)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Add Product'})

@user_passes_test(lambda u: u.is_staff)
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Update Product'})

@user_passes_test(lambda u: u.is_staff)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('product_list')
    return render(request, 'store/delete_product.html', {'product': product})

@user_passes_test(lambda u: u.is_staff)
def import_products(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process your CSV here
            messages.success(request, "Products imported successfully!")
            return redirect('product_list')
    else:
        form = CSVUploadForm()
    return render(request, 'store/import_products.html', {'form': form})

# ---------------------------------------------------------
# Cart Operations
# ---------------------------------------------------------
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart

def cart(request):
    total = 0
    quantity = 0
    cart_items = None
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart_obj = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart_obj, is_active=True)
            
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except Cart.DoesNotExist:
        pass
        
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            product=product,
            user=request.user,
            defaults={'quantity': 1}
        )
        if not created:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.warning(request, f"Only {product.stock} items available in stock.")
                return redirect('cart')
    else:
        try:
            cart_obj = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart_obj = Cart.objects.create(cart_id=_cart_id(request))
        cart_obj.save()
        
        cart_item, created = CartItem.objects.get_or_create(
            product=product,
            cart=cart_obj,
            defaults={'quantity': 1}
        )
        if not created:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.warning(request, f"Only {product.stock} items available in stock.")
                return redirect('cart')
            
    messages.success(request, f"{product.product_name} added to cart.")
    return redirect('cart')

def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user)
        else:
            cart_obj = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart_obj)
            
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass
    return redirect('cart')

def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user)
        else:
            cart_obj = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart_obj)
        cart_item.delete()
        messages.success(request, f"{product.product_name} removed from cart.")
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass
    return redirect('cart')

def update_cart_item(request, product_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            product = get_object_or_404(Product, id=product_id)
            if request.user.is_authenticated:
                cart_item = CartItem.objects.get(product=product, user=request.user)
            else:
                cart_obj = Cart.objects.get(cart_id=_cart_id(request))
                cart_item = CartItem.objects.get(product=product, cart=cart_obj)
            
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
        except (Cart.DoesNotExist, CartItem.DoesNotExist, ValueError):
            pass
    return redirect('cart')

# ---------------------------------------------------------
# Checkout & Orders
# ---------------------------------------------------------
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('product_list')
        
    original_total = 0
    total = 0
    quantity = 0
    total_delivery_charge = 0
    
    for cart_item in cart_items:
        orig_price = cart_item.product.original_price if cart_item.product.original_price else cart_item.product.price
        original_total += (orig_price * cart_item.quantity)
        
        subtotal = cart_item.product.price * cart_item.quantity
        total += subtotal
        
        delivery_charge_per_unit = 10 if cart_item.product.price < 20 else 0
        delivery_charge = delivery_charge_per_unit * cart_item.quantity
        total_delivery_charge += delivery_charge
        
        cart_item.original_price_val = orig_price
        cart_item.delivery_charge = delivery_charge
        cart_item.subtotal_with_delivery = subtotal + delivery_charge
        
        quantity += cart_item.quantity
        
    discount = original_total - total
    final_total = total + total_delivery_charge
    
    context = {
        'original_total': original_total,
        'discount': discount,
        'total_delivery_charge': total_delivery_charge,
        'total': final_total,
        'subtotal': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'store/checkout.html', context)

@login_required
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    if not cart_items.exists():
        return redirect('cart')
        
    if request.method == 'POST':
        total = 0
        total_delivery_charge = 0
        for item in cart_items:
            subtotal = item.product.price * item.quantity
            total += subtotal
            
            delivery_charge_per_unit = 10 if item.product.price < 20 else 0
            total_delivery_charge += (delivery_charge_per_unit * item.quantity)
            
        final_total = total + total_delivery_charge
        
        payment_method = request.POST.get('payment_method', 'COD')
        
        order = Order()
        order.user = request.user
        order.first_name = request.POST.get('first_name', '')
        order.last_name = request.POST.get('last_name', '')
        order.phone = request.POST.get('phone', '')
        order.email = request.POST.get('email', '')
        order.address = request.POST.get('address', '')
        order.city = request.POST.get('city', '')
        order.state = request.POST.get('state', '')
        order.country = request.POST.get('country', '')
        order.order_total = final_total
        order.status = 'Completed' if payment_method != 'COD' else 'Pending'
        order.is_ordered = True
        order.save()
        
        # Generate Order Number based on date and order ID
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")
        order.order_number = current_date + str(order.id)
        order.save()
        
        # Move Cart Items to Order Items, reduce stock, and set ordered to True
        for item in cart_items:
            order_item = OrderItem()
            order_item.order = order
            order_item.product = item.product
            order_item.quantity = item.quantity
            order_item.product_price = item.product.price
            order_item.ordered = True
            order_item.save()
            
            # Reduce stock
            product = item.product
            product.stock -= item.quantity
            product.save()
            
        # Clear cart upon successful order
        cart_items.delete()
        
        messages.success(request, f"Order placed successfully via {payment_method}.")
        return redirect('order_success', order_number=order.order_number)
        
    return redirect('checkout')

@login_required
def payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    original_total = 0
    total_delivery_charge = 0
    subtotal = 0
    
    for item in order_items:
        orig_price = item.product.original_price if item.product.original_price else item.product_price
        original_total += (orig_price * item.quantity)
        
        delivery_charge_per_unit = 10 if item.product_price < 20 else 0
        total_delivery_charge += (delivery_charge_per_unit * item.quantity)
        
        subtotal += item.product_price * item.quantity
        
    discount = original_total - subtotal
    
    context = {
        'order': order,
        'order_items': order_items,
        'original_total': original_total,
        'discount': discount,
        'total_delivery_charge': total_delivery_charge,
        'subtotal': subtotal,
    }
    return render(request, 'store/payment.html', context)

@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    original_total = 0
    total_delivery_charge = 0
    subtotal = 0
    
    for item in order_items:
        orig_price = item.product.original_price if item.product.original_price else item.product_price
        original_total += (orig_price * item.quantity)
        
        delivery_charge_per_unit = 10 if item.product_price < 20 else 0
        total_delivery_charge += (delivery_charge_per_unit * item.quantity)
        
        subtotal += item.product_price * item.quantity
        
    discount = original_total - subtotal
    
    context = {
        'order': order,
        'order_items': order_items,
        'original_total': original_total,
        'discount': discount,
        'total_delivery_charge': total_delivery_charge,
        'subtotal': subtotal,
    }
    return render(request, 'store/order_success.html', context)

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        product=product,
        user=request.user,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('checkout')

# ---------------------------------------------------------
# Wishlist
# ---------------------------------------------------------
@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"{product.product_name} added to your wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
def remove_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"{product.product_name} removed from your wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'wishlist_view'))

# ---------------------------------------------------------
# Order Returns & Cancellations
# ---------------------------------------------------------
@login_required
def request_return(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Ensure the order is actually eligible for a return
    if not order.can_be_returned():
        messages.error(request, "This order is no longer eligible for a return.")
        return redirect('home')
        
    form = OrderReturnForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        return_req = form.save(commit=False)
        return_req.order = order
        return_req.user = request.user
        return_req.save()
        messages.success(request, "Return requested successfully.")
        return redirect('home')
    return render(request, 'store/request_return.html', {'form': form, 'order': order})

@login_required
def request_cancellation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Ensure only pending orders can be cancelled
    if order.status != 'Pending':
        messages.error(request, "Only pending orders can be cancelled.")
        return redirect('home')
        
    # Prevent IntegrityError on double submission (OneToOne relationship constraint)
    if hasattr(order, 'cancellation'):
        messages.error(request, "A cancellation request already exists for this order.")
        return redirect('home')

    form = OrderCancellationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cancellation = form.save(commit=False)
        cancellation.order = order
        # OrderCancellation model strictly requires a refund_amount
        cancellation.refund_amount = order.order_total
        cancellation.save()
        messages.success(request, "Cancellation requested successfully.")
        return redirect('home')
    return render(request, 'store/request_cancellation.html', {'form': form, 'order': order})

# ---------------------------------------------------------
# Saved Searches
# ---------------------------------------------------------
@login_required
def saved_searches_list(request):
    searches = SavedSearch.objects.filter(user=request.user).select_related('category')
    return render(request, 'store/saved_searches.html', {'searches': searches})

@login_required
def save_search(request):
    if request.method == 'POST':
        form = SavedSearchForm(request.POST)
        if form.is_valid():
            search = form.save(commit=False)
            search.user = request.user
            search.save()
            messages.success(request, 'Search saved successfully!')
    return redirect('saved_searches')

@login_required
def delete_saved_search(request, search_id):
    search = get_object_or_404(SavedSearch, id=search_id, user=request.user)
    search.delete()
    messages.success(request, 'Saved search deleted.')
    return redirect('saved_searches')

# ---------------------------------------------------------
# Reviews
# ---------------------------------------------------------
@login_required
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        # Check if the product has been delivered to this user
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__is_ordered=True,
            order__status='Delivered'
        ).exists()
        if not can_review:
            messages.error(request, 'You can only review products that have been delivered to you.')
            return redirect(url)
            
        try:
            review = Review.objects.get(user=request.user, product=product)
            form = ReviewForm(request.POST, request.FILES, instance=review)
            msg = 'Your review has been updated and is pending moderation.'
        except Review.DoesNotExist:
            form = ReviewForm(request.POST, request.FILES)
            msg = 'Thank you! Your review has been submitted and is pending moderation.'
            
        if form.is_valid():
            data = form.save(commit=False)
            data.product = product
            data.user = request.user
            data.approved = True
            data.save()
            
            ReviewModeration.objects.update_or_create(
                review=data,
                defaults={'status': 'Approved'}
            )
            messages.success(request, msg)
            return redirect(url)
        else:
            messages.error(request, 'There was a problem submitting your review. Please check your inputs.')
    return redirect(url)

# ---------------------------------------------------------
# Review Moderation (Staff Only)
# ---------------------------------------------------------
@user_passes_test(lambda u: u.is_staff)
def review_moderation_list(request):
    moderations = ReviewModeration.objects.select_related('review', 'review__product').order_by('-created_at')
    return render(request, 'store/review_moderation.html', {'moderations': moderations})

@user_passes_test(lambda u: u.is_staff)
def moderate_review(request, moderation_id):
    moderation = get_object_or_404(ReviewModeration, id=moderation_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['approve', 'reject']:
            if action == 'approve':
                moderation.status = 'Approved'
                moderation.review.approved = True
            elif action == 'reject':
                moderation.status = 'Rejected'
                moderation.reason_for_rejection = request.POST.get('reason_for_rejection', '')
                moderation.review.approved = False
            moderation.moderator = request.user
            moderation.review.save()
            moderation.save()
            messages.success(request, f'Review {action}d successfully.')
        else:
            messages.error(request, 'Invalid moderation action provided.')
    return redirect('review_moderation')

# ---------------------------------------------------------
# Coupons
# ---------------------------------------------------------
# @login_required
# def apply_coupon(request):
#     if request.method == 'POST':
#         code = request.POST.get('coupon_code')
#         try:
#             coupon = Coupon.objects.get(code__iexact=code, active=True)
#             if coupon.valid_from <= datetime.date.today() <= coupon.valid_to:
#                 request.session['coupon_id'] = coupon.id
#                 messages.success(request, f"Coupon '{code}' applied successfully!")
#             else:
#                 messages.error(request, "This coupon has expired or is not valid yet.")
#         except Coupon.DoesNotExist:
#             messages.error(request, "Invalid coupon code.")
#     return redirect('checkout')

# ---------------------------------------------------------
# Order Tracking
# ---------------------------------------------------------
def track_order(request):
    order = None
    if request.method == 'GET' and 'order_number' in request.GET:
        order_number = request.GET.get('order_number')
        try:
            if request.user.is_authenticated:
                order = Order.objects.get(order_number=order_number, user=request.user)
            else:
                messages.error(request, "Please log in to track your order.")
                return redirect('login')
        except Order.DoesNotExist:
            messages.error(request, "Order not found. Please check your order number.")
    return render(request, 'store/track_order.html', {'order': order})

# ---------------------------------------------------------
# Payments Integration
# ---------------------------------------------------------
@login_required
def process_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if request.method == 'POST':
        payment_method = request.POST.get('paymentMethod', 'COD')
        
        order.status = 'Completed' if payment_method != 'COD' else 'Pending'
        order.is_ordered = True
        order.save()
        
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            item.ordered = True
            item.save()
            # Reduce stock
            product = item.product
            product.stock -= item.quantity
            product.save()
            
        # Clear cart upon successful order
        CartItem.objects.filter(user=request.user, is_active=True).delete()
        
        messages.success(request, f"Order placed successfully via {payment_method}.")
        return redirect('order_success', order_number=order.order_number)
    return redirect('payment', order_number=order.order_number)
