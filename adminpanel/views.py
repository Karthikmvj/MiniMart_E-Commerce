from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from store.models import Product, Order, Category
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils import timezone
from .forms import ProductForm, CategoryForm, AdminProfileForm, SystemSettingsForm, AdminSignupForm
from .models import SystemSettings


def is_admin(user):
    return user.is_authenticated and user.is_active and user.is_staff

def admin_required(view_func):
    return user_passes_test(is_admin, login_url='adminpanel:login')(view_func)

# Custom Authentication Views
def login_view(request):
    if request.user.is_authenticated and request.user.is_active and request.user.is_staff:
        return redirect('adminpanel:dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                auth_login(request, user)
                
                # Handle Remember Me
                remember_me = request.POST.get('remember_me')
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser close
                
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('adminpanel:dashboard')
            else:
                messages.error(request, 'Access denied. You do not have administrator permissions.')
                return redirect('adminpanel:login')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
        
    return render(request, 'adminpanel/login.html', {'form': form})

def signup_view(request):
    if request.user.is_authenticated and request.user.is_active and request.user.is_staff:
        return redirect('adminpanel:dashboard')
        
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Admin account created successfully! Please sign in.')
            return redirect('adminpanel:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminSignupForm()
        
    return render(request, 'adminpanel/signup.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('adminpanel:login')

# Dashboard View
@admin_required
def dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    
    recent_products = Product.objects.all().order_by('-id')[:5]
    recent_orders = Order.objects.select_related('user').order_by('-id')[:5]
    
    order_statuses = list(Order.objects.values('status').annotate(count=Count('id')))
    status_labels = [item['status'] for item in order_statuses]
    status_values = [item['count'] for item in order_statuses]
    
    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    
    sales_query = (
        Order.objects.filter(created_at__date__gte=today - timedelta(days=6))
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(total=Sum('order_total'))
    )
    sales_map = {item['date']: float(item['total'] or 0) for item in sales_query if item['date']}
    
    sales_labels = [day.strftime('%b %d') for day in last_7_days]
    sales_values = [sales_map.get(day, 0.0) for day in last_7_days]
    
    category_counts = list(Category.objects.annotate(p_count=Count('product')).values('category_name', 'p_count'))
    for item in category_counts:
        item['percentage'] = (item['p_count'] / total_products * 100) if total_products > 0 else 0
    cat_labels = [item['category_name'] for item in category_counts]
    cat_values = [item['p_count'] for item in category_counts]
    
    sales_total = sum(sales_values)
    sales_avg = sales_total / len(sales_values) if sales_values else 0
    sales_peak_val = max(sales_values) if sales_values else 0
    sales_peak_index = sales_values.index(sales_peak_val) if sales_values and sales_peak_val > 0 else -1
    sales_peak_day = sales_labels[sales_peak_index] if sales_peak_index != -1 else 'N/A'

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'recent_products': recent_products,
        'recent_orders': recent_orders,
        'status_labels': status_labels,
        'status_values': status_values,
        'sales_labels': sales_labels,
        'sales_values': sales_values,
        'cat_labels': cat_labels,
        'cat_values': cat_values,
        'sales_total': sales_total,
        'sales_avg': sales_avg,
        'sales_peak_val': sales_peak_val,
        'sales_peak_day': sales_peak_day,
        'order_statuses': order_statuses,
        'category_counts': category_counts,
    }
    
    return render(request, 'adminpanel/dashboard.html', context)

from .forms import OfferForm
from store.models import Offer

# Offer CRUD Views
@admin_required
def offer_list(request):
    offers = Offer.objects.all().order_by('-id')
    return render(request, 'adminpanel/offers.html', {'offers': offers})

@admin_required
def add_offer(request):
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offer added successfully!')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('adminpanel:offer_list')
    else:
        form = OfferForm()
    return render(request, 'adminpanel/add_offer.html', {'form': form})

@admin_required
def edit_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offer updated successfully!')
            return redirect('adminpanel:offer_list')
    else:
        form = OfferForm(instance=offer)
    return render(request, 'adminpanel/edit_offer.html', {'form': form, 'offer': offer})

@admin_required
def delete_offer(request, id):
    offer = get_object_or_404(Offer, id=id)
    if request.method == 'POST':
        offer.delete()
        messages.success(request, 'Offer deleted successfully!')
        return redirect('adminpanel:offer_list')
    return render(request, 'adminpanel/delete_offer.html', {'offer': offer})

# Profile & Settings Views
@admin_required
def profile_view(request):
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('adminpanel:profile')
    else:
        form = AdminProfileForm(instance=request.user)
    return render(request, 'adminpanel/profile.html', {'form': form})

@admin_required
def settings_view(request):
    settings_obj, created = SystemSettings.objects.get_or_create(id=1)
    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'System settings updated successfully!')
            return redirect('adminpanel:settings')
    else:
        form = SystemSettingsForm(instance=settings_obj)
    return render(request, 'adminpanel/settings.html', {'form': form, 'settings': settings_obj})

# Category CRUD Views
@admin_required
def category_list(request):
    categories = Category.objects.all().order_by('id')
    return render(request, 'adminpanel/category_list.html', {'categories': categories})

@admin_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('adminpanel:category_list')
    else:
        form = CategoryForm()
    return render(request, 'adminpanel/add_category.html', {'form': form})

@admin_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('adminpanel:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'adminpanel/edit_category.html', {'form': form, 'category': category})

@admin_required
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('adminpanel:category_list')
    return render(request, 'adminpanel/delete_category.html', {'category': category})

# Product CRUD Views
@admin_required
def product_list(request):
    products = Product.objects.all().select_related('category').order_by('-id')
    categories = Category.objects.all().order_by('category_name')
    
    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        
    if category_id:
        products = products.filter(category_id=category_id)
        
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
    }
    return render(request, 'adminpanel/products.html', context)

@admin_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('adminpanel:product_list')
    else:
        form = ProductForm()
    return render(request, 'adminpanel/add_product.html', {'form': form})

@admin_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('adminpanel:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'adminpanel/edit_product.html', {'form': form, 'product': product})

@admin_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('adminpanel:product_list')
    return render(request, 'adminpanel/delete_product.html', {'product': product})

# Stock & Orders Views
@admin_required
def update_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        stock = request.POST.get('stock')
        try:
            stock = int(stock)
            if stock < 0:
                messages.error(request, 'Stock cannot be negative.')
            else:
                product.stock = stock
                product.is_available = stock > 0
                product.save(update_fields=['stock', 'is_available'])
                messages.success(request, 'Stock updated successfully!')
                return redirect('adminpanel:product_list')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid stock value.')
    return render(request, 'adminpanel/update_stock.html', {'product': product})

@admin_required
def stock_management(request):
    products = Product.objects.all().order_by('stock')
    low_stock_count = products.filter(stock__lt=10, stock__gt=0).count()
    out_of_stock_count = products.filter(stock=0).count()
    context = {
        'products': products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }
    return render(request, 'adminpanel/stock_management.html', context)

@admin_required
def order_list(request):
    orders = Order.objects.select_related('user').order_by('-id')
    
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
        
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    context = {
        'orders': orders,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Order.STATUS,
    }
    return render(request, 'adminpanel/orders.html', context)


@admin_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all().select_related('product')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS):
            old_status = order.status
            if new_status != old_status:
                order.status = new_status
                order.save()
                
                # Auto-restock if status changes to Cancelled
                if new_status == 'Cancelled':
                    for item in items:
                        item.product.stock += item.quantity
                        if item.product.stock > 0:
                            item.product.is_available = True
                        item.product.save(update_fields=['stock', 'is_available'])
                    messages.success(request, f'Order status updated to Cancelled and items restocked.')
                else:
                    messages.success(request, f'Order status updated to {new_status} successfully!')
            return redirect('adminpanel:order_detail', order_id=order.id)
            
    return render(request, 'adminpanel/order_detail.html', {'order': order, 'items': items, 'status_choices': Order.STATUS})


@admin_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    search_query = request.GET.get('search', '')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
        
    context = {'users': users, 'search_query': search_query}
    return render(request, 'adminpanel/users.html', context)

def forgot_password(request):
    # If admin is already logged in, skip email verification and go straight to reset
    if request.user.is_authenticated and request.user.is_active and request.user.is_staff:
        request.session['admin_reset_user_id'] = request.user.id
        messages.success(request, 'Please enter your new administrator password.')
        return redirect('adminpanel:reset_password')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = User.objects.filter(email=email, is_staff=True).first()
        if user:
            request.session['admin_reset_user_id'] = user.id
            messages.success(request, 'Email verified! Please enter your new administrator password.')
            return redirect('adminpanel:reset_password')
        else:
            messages.error(request, 'No administrator account found with that email address.')
    return render(request, 'adminpanel/forgot_password.html')

def reset_password(request):
    user_id = request.session.get('admin_reset_user_id')
    if not user_id:
        messages.error(request, 'Session expired or invalid request. Please start again.')
        return redirect('adminpanel:forgot_password')
        
    user = get_object_or_404(User, id=user_id, is_staff=True)
    is_logged_in = request.user.is_authenticated and request.user.is_active and request.user.is_staff
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if not password or not confirm_password:
            messages.error(request, 'Please fill in all fields.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match!')
        else:
            user.set_password(password)
            user.save()
            # Clean up session
            del request.session['admin_reset_user_id']
            if is_logged_in:
                # Re-login so the session stays valid after password change
                auth_login(request, user)
                messages.success(request, 'Your password has been successfully reset.')
                return redirect('adminpanel:profile')
            else:
                messages.success(request, 'Administrator password has been successfully reset. Please sign in with your new password.')
                return redirect('adminpanel:login')
            
    return render(request, 'adminpanel/reset_password.html')