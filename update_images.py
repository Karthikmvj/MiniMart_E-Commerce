import os
import urllib.request
import django
from pathlib import Path

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniMart.settings')
django.setup()

from store.models import Product, Category
from django.conf import settings

# Explicit, curated mapping to Unsplash image IDs that perfectly match the names of products
UNSPLASH_IDS = {
    "Wireless Mouse": "photo-1615663245857-ac93bb7c39e7",
    "Mechanical Keyboard": "photo-1595225476474-87563907a212",
    "Bluetooth Headphones": "photo-1505740420928-5e560c06d30e",
    "Samsung Galaxy A35": "photo-1610945265064-0e34e5519bbf",
    "HP 15Laptop": "photo-1588872657578-7efd1f1555ed",
    "Lenovo IdeaPad Slim 3": "photo-1593642632823-8f785ba67e45",
    "Aura Smart Phone": "photo-1511707171634-5f897ff02aa9",
    "Nova Laptop Pro": "photo-1603302576837-37561b2e2302",
    "Pulse Wireless Earbuds": "photo-1590658268037-6bf12165a8df",
    "Orbit Smart Watch": "photo-1508685096489-7aacd43bd3b1",
    "Crest 4K Television": "photo-1593305841991-05c297ba4575",
    "Lumen Bluetooth Speaker": "photo-1608043152269-423dbba4e7e1",
    "Atlas Gaming Headset": "photo-1606144042614-b2417e99c4e3",
    "Flex Running Shoes": "photo-1542291026-7eec264c27ff",
    "Sora Denim Jacket": "photo-1576995853123-5a10305d93c0",
    "Mira Cotton Kurti": "photo-1610030469983-98e550d6193c",
    "Vega Formal Shirt": "photo-1596755094514-f87e34085b2c",
    "Echo Leather Belt": "photo-1553062407-98eeb64c6a62",
    "Chic Tote Bag": "photo-1544816155-12df9643f363",
    "Oven Fresh Coffee Maker": "photo-1495474472287-4d71bcdd2085",
    "Glow Blender": "photo-1578643463396-0997cb5328c1",
    "Harbor Microwave Oven": "photo-1574269909862-7e1d70bb8078",
    "Stoneware Dinner Set": "photo-1610701596007-11502861dcfa",
    "Aero Vacuum Cleaner": "photo-1558317374-067fb5f30001",
    "PureGlow Face Serum": "photo-1608248597279-f99d160bfcbc",
    "SilkCare Shampoo": "photo-1535585209827-a15fcdbc4c2d",
    "Velvet Moisturizer": "photo-1601049541289-9b1b7bbbfe19",
    "FitPulse Resistance Band": "photo-1517838277536-f5f99be501cd",
    "Sprint Yoga Mat": "photo-1601925260368-ae2f83cf8b7f",
    "Peak Water Bottle": "photo-1602143407151-7111542de6e8",
    "Daily Fresh Olive Oil": "photo-1474979266404-7eaacbcd87c5",
    "Nova 12 Pro": "photo-1598327105666-5b89351aff97",
    "Pixel Lite 5G": "photo-1580910051074-3eb694886505",
    "Urban Hoodie": "photo-1556821840-3a63f95609a7",
    "Satin Party Dress": "photo-1595777457583-95e059d581b8",
    "Aura Smart Watch": "photo-1579586337278-3befd40fd17a",
    "Pulse Bluetooth Speaker": "photo-1589003077984-894e133dabab",
    "Fresh Farm Milk": "photo-1563636619-e9143da7973b",
    "Organic Green Tea": "photo-1597481499750-3e6b22637e12",
    "Glow Face Serum": "photo-1620916566398-39f1143ab7be",
    "Pro Yoga Mat": "photo-1592432678016-e910b452f9a2",
    "Sprint Running Shoes": "photo-1608231387042-66d1773070a5",
    "Leather Passport Holder": "photo-1590874103328-eac38a683ce7",
    "Stainless Steel Lunch Box": "photo-1534422298391-e4f8c172dddb",
    "Detox Green Juice": "photo-1540420773420-3366772f4999",
    "Organic Fresh Vegetables": "photo-1566385101042-1a0aa0c1268c",
}

# Explicit, curated mapping to Unsplash image IDs for the store categories
UNSPLASH_CAT_IDS = {
    "Electronics": "photo-1498049794561-7780e7231661",
    "Accessories": "photo-1523275335684-37898b6baf30",
    "Audios": "photo-1484704849700-f032a568e944",
    "Mobile": "photo-1511707171634-5f897ff02aa9",
    "Mobiles": "photo-1511707171634-5f897ff02aa9",
    "Laptop": "photo-1588872657578-7efd1f1555ed",
    "Fashion": "photo-1483985988355-763728e1935b",
    "Clothing": "photo-1483985988355-763728e1935b",
    "Home & Kitchen": "photo-1556911220-e15b29be8c8f",
    "Home-Kitchen": "photo-1556911220-e15b29be8c8f",
    "Health & Beauty": "photo-1596462502278-27bfdc403348",
    "Beauty": "photo-1596462502278-27bfdc403348",
    "Sports & Fitness": "photo-1476480862126-209bfaa8edc8",
    "Sports": "photo-1476480862126-209bfaa8edc8",
    "Groceries": "photo-1542838132-92c53300491e",
}

def download_image(photo_id, name, is_category=False):
    folder = "categories" if is_category else "products"
    safe_name = name.lower().replace(' ', '_').replace('-', '_').replace('&', 'and')
    filename = f"photos/{folder}/{safe_name}.jpg"
    target_path = Path(settings.MEDIA_ROOT) / filename
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Unsplash Source Direct CDN URL
    url = f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=600&h=600&q=80"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(target_path, 'wb') as f:
                f.write(response.read())
        print(f"[{'Category' if is_category else 'Product'}] Downloaded '{name}' successfully.")
        return filename
    except Exception as e:
        print(f"[{'Category' if is_category else 'Product'}] Failed to download '{name}': {e}")
        return None

def update_all_images():
    print("=== STARTING PRODUCT AND CATEGORY IMAGE RESET ===")
    
    # 1. Update Product Images
    products = Product.objects.all()
    prod_success = 0
    for p in products:
        name = p.product_name
        photo_id = UNSPLASH_IDS.get(name)
        if photo_id:
            filename = download_image(photo_id, name, is_category=False)
            if filename:
                p.images = filename
                p.save()
                prod_success += 1
        else:
            print(f"[Product] Warning: No Unsplash ID mapped for '{name}'")
            
    # 2. Update Category Images
    categories = Category.objects.all()
    cat_success = 0
    for c in categories:
        name = c.category_name
        photo_id = UNSPLASH_CAT_IDS.get(name)
        if photo_id:
            filename = download_image(photo_id, name, is_category=True)
            if filename:
                c.category_image = filename
                c.save()
                cat_success += 1
        else:
            print(f"[Category] Warning: No Unsplash ID mapped for '{name}'")
            
    print(f"=== COMPLETED! Product updates: {prod_success}/{len(products)} | Category updates: {cat_success}/{len(categories)} ===")

if __name__ == '__main__':
    update_all_images()
