from django.urls import path
from . import views
from . import utils

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('set-language/<str:language_code>/', utils.set_language_and_redirect, name='set_language_and_redirect'),

    # Profile & Account
    path('profile/', views.profile, name='profile'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('settings/', views.settings_view, name='settings_view'),
    path('password/change/', views.change_password, name='change_password'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),

    # Address Management
    path('addresses/', views.address_book, name='address_book'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/<int:address_id>/edit/', views.edit_address, name='edit_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    
    # Payment Methods
    path('payments/', views.payment_methods, name='payment_methods'),
    path('payments/add/', views.add_payment_method, name='add_payment_method'),
    path('payments/<int:method_id>/delete/', views.delete_payment_method, name='delete_payment_method'),
    
    # Notification Preferences
    path('notifications/', views.notification_preferences, name='notification_preferences'),
    
    # Forgot Password Flow
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
]