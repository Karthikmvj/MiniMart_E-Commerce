from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .forms import RegistrationForm, AddressForm, PaymentMethodForm, NotificationPreferenceForm
from .models import Address, PaymentMethod, NotificationPreference, UserProfile
from store.models import Order, WishlistItem

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, _('Registration successful! You can now log in.'))
            return redirect('login')
    else:
        form = RegistrationForm()
        
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Handle Remember Me
            remember_me = request.POST.get('remember_me')
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Browser close
                
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, _('Invalid username or password.'))
    else:
        form = AuthenticationForm()
        
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, _('Logout Successful! Thank you for shopping with MiniMart. See you again!'))
    return redirect('login')

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    recent_orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')[:3]
    
    # Calculate profile stats
    total_orders_count = Order.objects.filter(user=request.user, is_ordered=True).count()
    wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    
    # Fetch default shipping address (fallback to first available if no default is explicitly marked)
    default_address = Address.objects.filter(user=request.user, is_default=True).first()
    if not default_address:
        default_address = Address.objects.filter(user=request.user).first()
        
    context = {
        'user_profile': user_profile,
        'recent_orders': recent_orders,
        'total_orders_count': total_orders_count,
        'wishlist_count': wishlist_count,
        'default_address': default_address,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_settings(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        user_profile.mobile_number = request.POST.get('mobile_number', user_profile.mobile_number)
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
        user_profile.save()
            
        messages.success(request, _('Profile updated successfully.'))
        return redirect('profile')
    return render(request, 'accounts/profile_settings.html', {'user_profile': user_profile})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Your password was successfully updated!'))
            return redirect('profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form, 'title': _('Change Password')})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'accounts/order_history.html', {'orders': orders})

@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, is_ordered=True)
    order_items = order.items.select_related('product', 'product__brand').all()

    # Calculate line totals for each item
    subtotal = 0
    for item in order_items:
        item.line_total = item.product_price * item.quantity
        subtotal += item.line_total

    context = {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_invoice.html', context)

@login_required
def address_book(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/address_book.html', {'addresses': addresses})

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, _('Address added successfully.'))
            return redirect('address_book')
    else:
        form = AddressForm()
    return render(request, 'accounts/add_address.html', {'form': form})

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, _('Address updated successfully.'))
            return redirect('address_book')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/edit_address.html', {'address': address, 'form': form})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('address_book')
    return render(request, 'accounts/delete_address.html', {'address': address})

@login_required
def payment_methods(request):
    methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
    return render(request, 'accounts/payment_methods.html', {'methods': methods})

@login_required
def add_payment_method(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.save()
            return redirect('payment_methods')
    else:
        form = PaymentMethodForm()
    return render(request, 'accounts/add_payment_method.html', {'form': form})

@login_required
def delete_payment_method(request, method_id):
    method = get_object_or_404(PaymentMethod, id=method_id, user=request.user)
    if request.method == 'POST':
        method.is_active = False
        method.save()
        return redirect('payment_methods')
    return render(request, 'accounts/delete_payment_method.html', {'method': method})

@login_required
def notification_preferences(request):
    preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = NotificationPreferenceForm(instance=preferences)
    return render(request, 'accounts/notification_preferences.html', {'preferences': preferences, 'form': form})

# 2FA setup and verify views removed

@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html', {'title': _('Account Settings')})

from django.contrib.auth.models import User

def forgot_password(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = User.objects.filter(email=email).first()
        if user:
            request.session['reset_user_id'] = user.id
            messages.success(request, _('Email verified! Please enter your new password.'))
            return redirect('reset_password')
        else:
            messages.error(request, _('No user account found with that email address.'))
    return render(request, 'accounts/forgot_password.html')

def reset_password(request):
    if request.user.is_authenticated:
        return redirect('home')
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, _('Session expired or invalid request. Please start again.'))
        return redirect('forgot_password')
        
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if not password or not confirm_password:
            messages.error(request, _('Please fill in all fields.'))
        elif password != confirm_password:
            messages.error(request, _('Passwords do not match!'))
        else:
            user.set_password(password)
            user.save()
            # Clean up session
            del request.session['reset_user_id']
            messages.success(request, _('Your password has been successfully reset. Please login with your new password.'))
            return redirect('login')
            
    return render(request, 'accounts/reset_password.html')