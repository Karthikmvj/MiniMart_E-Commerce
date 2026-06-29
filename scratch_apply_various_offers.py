import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniMart.settings')
django.setup()

from store.models import Offer, Product

def apply_various_offers():
    today = date.today()
    
    # Define 5 different offers
    offers_data = [
        {"title": "Summer Sale", "discount": 10},
        {"title": "Special Deal", "discount": 15},
        {"title": "Super Deal", "discount": 20},
        {"title": "Mega Saver", "discount": 30},
        {"title": "Clearance Sale", "discount": 50},
    ]
    
    offers = []
    for data in offers_data:
        offer, created = Offer.objects.get_or_create(
            title=data["title"],
            defaults={
                "description": f"Get {data['discount']}% off on selected items!",
                "discount_percentage": data["discount"],
                "start_date": today - timedelta(days=5),
                "end_date": today + timedelta(days=30),
                "active": True
            }
        )
        if not created:
            offer.discount_percentage = data["discount"]
            offer.start_date = today - timedelta(days=5)
            offer.end_date = today + timedelta(days=30)
            offer.active = True
            offer.save()
        offers.append(offer)
        print(f"Offer ready: {offer.title} ({offer.discount_percentage}% OFF)")

    # Distribute offers to all products
    products = Product.objects.all()
    print(f"\nDistributing various offers to {products.count()} products...")
    
    # Use a fixed seed for deterministic/even distribution
    random.seed(42)
    
    for product in products:
        # Determine base price
        base_price = product.original_price if product.original_price else product.price
        
        # Reset original_price to base_price, and reset price to base_price before applying new offer
        product.original_price = base_price
        product.price = base_price
        
        # Choose a random offer from our list
        chosen_offer = random.choice(offers)
        product.offer = chosen_offer
        product.save()
        print(f"- '{product.product_name}': Original: {product.original_price} -> Offer Price: {product.price} ({chosen_offer.discount_percentage}% OFF via {chosen_offer.title})")

if __name__ == '__main__':
    apply_various_offers()
