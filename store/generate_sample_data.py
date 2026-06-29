import os
import django
from django.utils.text import slugify
import random

import sys
from pathlib import Path
# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniMart.settings')
django.setup()

from store.models import Product, Brand, Color

def seed_brands_and_colors():
    print("Seeding Brands and Colors...")
    
    # Define Brands
    brands_data = [
        "Samsung", "HP", "Lenovo", "Apple", "Nike", "Orbit", "Crest",
        "Lumen", "Vega", "Oven Fresh", "Harbor", "PureGlow", "FitPulse",
        "Nova", "Sony", "LG", "Philips", "Dell", "Asus", "Puma", "Adidas"
    ]
    
    brands = {}
    for b_name in brands_data:
        brand, created = Brand.objects.get_or_create(
            brand_name=b_name,
            defaults={'slug': slugify(b_name)}
        )
        brands[b_name] = brand
        if created:
            print(f"Created Brand: {b_name}")

    # Define Colors
    colors_data = [
        ("Red", "#FF0000"),
        ("Blue", "#0000FF"),
        ("Green", "#008000"),
        ("Black", "#000000"),
        ("White", "#FFFFFF"),
        ("Gold", "#FFD700"),
        ("Silver", "#C0C0C0"),
        ("Yellow", "#FFFF00"),
        ("Pink", "#FFC0CB")
    ]
    
    colors = []
    for c_name, c_code in colors_data:
        color, created = Color.objects.get_or_create(
            color_name=c_name,
            defaults={'color_code': c_code}
        )
        colors.append(color)
        if created:
            print(f"Created Color: {c_name} ({c_code})")

    # Assign Brands and Colors to existing products
    products = Product.objects.all()
    print(f"Assigning brands and colors to {products.count()} products...")
    
    for p in products:
        # Assign a brand if it doesn't have one
        if not p.brand:
            # Let's try to match brand by product name
            assigned_brand = None
            for b_name in brands_data:
                if b_name.lower() in p.product_name.lower():
                    assigned_brand = brands[b_name]
                    break
            if not assigned_brand:
                # Assign a random brand
                assigned_brand = random.choice(list(brands.values()))
            
            p.brand = assigned_brand
            p.save()
            print(f"Assigned Brand '{p.brand.brand_name}' to Product '{p.product_name}'")

        # Assign colors if it doesn't have any
        if p.colors.count() == 0:
            # Assign 1 to 3 random colors
            num_colors = random.randint(1, 3)
            p_colors = random.sample(colors, num_colors)
            p.colors.add(*p_colors)
            print(f"Assigned Colors {[c.color_name for c in p_colors]} to Product '{p.product_name}'")
            
    print("Finished seeding Brands and Colors.")

if __name__ == '__main__':
    seed_brands_and_colors()
