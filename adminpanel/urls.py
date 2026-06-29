from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # Dashboard & Auth
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile & Settings
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    
    # Offers
    path('offers/', views.offer_list, name='offer_list'),
    path('offers/add/', views.add_offer, name='add_offer'),
    path('offers/edit/<int:pk>/', views.edit_offer, name='edit_offer'),
    path('offers/delete/<int:id>/', views.delete_offer, name='delete_offer'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:id>/', views.delete_category, name='delete_category'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:id>/', views.delete_product, name='delete_product'),
    path('products/update-stock/<int:pk>/', views.update_stock, name='update_stock'),
    
    # Stock, Orders, Users
    path('stock/', views.stock_management, name='stock_management'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('users/', views.user_list, name='user_list'),
    
    # Forgot/Reset Password
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
]
