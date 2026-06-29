from django.db.models import Case, When
from .models import Category

def menu_links(request):
    # Order menu items: Fashion -> Electronics -> Groceries -> Beauty -> Sports
    # (Home is typically hardcoded in the template before the categories loop)
    preserved_order = Case(
        When(category_name__iexact='Fashion', then=1),
        When(category_name__iexact='Electronics', then=2),
        When(category_name__iexact='Groceries', then=3),
        When(category_name__iexact='Beauty', then=4),
        When(category_name__iexact='Sports', then=5),
        default=6
    )
    links = Category.objects.all().order_by(preserved_order)
    return dict(links=links)

from store.models import WishlistItem, CartItem, Cart
from store.views import _cart_id

def wishlist_and_cart_info(request):
    wishlist_product_ids = []
    wishlist_count = 0
    cart_count = 0
    
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(user=request.user)
        wishlist_product_ids = list(wishlist_items.values_list('product_id', flat=True))
        wishlist_count = wishlist_items.count()
        cart_count = sum(item.quantity for item in CartItem.objects.filter(user=request.user, is_active=True))
    else:
        # Check anonymous cart count
        cart_id = request.session.session_key
        if cart_id:
            try:
                cart_obj = Cart.objects.get(cart_id=cart_id)
                cart_count = sum(item.quantity for item in CartItem.objects.filter(cart=cart_obj, is_active=True))
            except Cart.DoesNotExist:
                pass
                
    return {
        'wishlist_product_ids': wishlist_product_ids,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    }
