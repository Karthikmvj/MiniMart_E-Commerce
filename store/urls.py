from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/category/<slug:category_slug>/', views.product_list, name='products_by_category'),
    path('search/', views.product_list, name='search'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.update_product, name='update_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('products/import/', views.import_products, name='import_products'),
    path('products/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_cart, name='add_cart'),
    path('cart/remove/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path('cart/remove_item/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/update_item/<int:product_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),
    path('payment/<str:order_number>/', views.payment, name='payment'),
    path('payment/process/<str:order_number>/', views.process_payment, name='process_payment'),
    path('order_success/<str:order_number>/', views.order_success, name='order_success'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:product_id>/', views.add_wishlist, name='add_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_wishlist, name='remove_wishlist'),
    path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),
    
    # Order Returns & Cancellations
    path('track-order/', views.track_order, name='track_order'),
    path('order/<int:order_id>/return/', views.request_return, name='request_return'),
    path('order/<int:order_id>/cancel/', views.request_cancellation, name='request_cancellation'),
    
    # Saved Searches
    path('saved-searches/', views.saved_searches_list, name='saved_searches'),
    path('save-search/', views.save_search, name='save_search'),
    path('saved-searches/<int:search_id>/delete/', views.delete_saved_search, name='delete_saved_search'),
    
    # Review Moderation (Staff Only)
    path('moderation/reviews/', views.review_moderation_list, name='review_moderation'),
    path('moderation/reviews/<int:moderation_id>/', views.moderate_review, name='moderate_review'),
]