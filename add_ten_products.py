import os
import urllib.request
import django
from pathlib import Path
from django.utils.text import slugify

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniMart.settings')
django.setup()

from store.models import Product, Category, ProductImage
from django.conf import settings

# 10 new products details
NEW_PRODUCTS = [
    {
        "name": "UltraHD Action Camera",
        "category_name": "Electronics",
        "price": 8999.00,
        "original_price": 11999.00,
        "stock": 20,
        "description": "A rugged, waterproof 4K action camera perfect for sports, travel, and outdoor adventures."
    },
    {
        "name": "Ergonomic Office Chair",
        "category_name": "Home & Kitchen",
        "price": 12499.00,
        "original_price": 15999.00,
        "stock": 15,
        "description": "Premium adjustable desk chair with ergonomic lumbar support and breathable mesh back."
    },
    {
        "name": "Smart Coffee Mug",
        "category_name": "Home & Kitchen",
        "price": 2499.00,
        "original_price": 3499.00,
        "stock": 35,
        "description": "Temperature-controlled smart mug to keep your coffee, tea, or cocoa hot all day."
    },
    {
        "name": "Noise Cancelling Earplugs",
        "category_name": "Accessories",
        "price": 999.00,
        "original_price": 1499.00,
        "stock": 50,
        "description": "High-fidelity earplugs designed to reduce volume while preserving sound clarity."
    },
    {
        "name": "Portable Charger 20000mAh",
        "category_name": "Electronics",
        "price": 1899.00,
        "original_price": 2499.00,
        "stock": 40,
        "description": "High-capacity external battery bank with high-speed charging ports for all mobile devices."
    },
    {
        "name": "Leather Passport Holder",
        "category_name": "Accessories",
        "price": 799.00,
        "original_price": 1199.00,
        "stock": 30,
        "description": "Handcrafted genuine leather travel wallet with compartments for passport, tickets, and cards."
    },
    {
        "name": "Stainless Steel Lunch Box",
        "category_name": "Home & Kitchen",
        "price": 699.00,
        "original_price": 999.00,
        "stock": 45,
        "description": "Eco-friendly, leakproof double-deck metal bento box for healthy school and office lunches."
    },
    {
        "name": "Organic Honey (500g)",
        "category_name": "Groceries",
        "price": 349.00,
        "original_price": 449.00,
        "stock": 60,
        "description": "100% pure, raw, and unfiltered natural forest honey packed with health benefits."
    },
    {
        "name": "Detox Green Juice",
        "category_name": "Groceries",
        "price": 149.00,
        "original_price": 199.00,
        "stock": 100,
        "description": "Fresh cold-pressed nutritional drink with cucumber, spinach, kale, apple, and lemon."
    },
    {
        "name": "Aromatherapy Diffuser",
        "category_name": "Beauty",
        "price": 1599.00,
        "original_price": 2199.00,
        "stock": 25,
        "description": "Ultrasonic cool-mist humidifier and essential oil diffuser with color-changing ambient LEDs."
    },
    {
        "name": "Organic Fresh Vegetables",
        "category_name": "Groceries",
        "price": 199.00,
        "original_price": 249.00,
        "stock": 50,
        "description": "Fresh and organic mixed vegetables, packed with nutrients and harvested daily."
    }
]

# Sets of 3 related Unsplash IDs for all 52 products (existing + new)
PRODUCT_UNSPLASH_SETS = {
    "Wireless Mouse": [
        "photo-1615663245857-ac93bb7c39e7", # main
        "photo-1625766763788-95dcce9bf5ac", # extra 1
        "photo-1615663246413-5807afb72bf6"  # extra 2
    ],
    "Mechanical Keyboard": [
        "photo-1595225476474-87563907a212",
        "photo-1618384887929-16ec33fab9ef",
        "photo-1601445638532-3c6f6c3aa1d6"
    ],
    "Bluetooth Headphones": [
        "photo-1505740420928-5e560c06d30e",
        "photo-1484704849700-f032a568e944",
        "photo-1546435770-a3e426bf472b"
    ],
    "Samsung Galaxy A35": [
        "photo-1610945265064-0e34e5519bbf",
        "photo-1598327105666-5b89351aff97",
        "photo-1511707171634-5f897ff02aa9"
    ],
    "HP 15Laptop": [
        "photo-1588872657578-7efd1f1555ed",
        "photo-1603302576837-37561b2e2302",
        "photo-1496181130204-755241544e35"
    ],
    "Lenovo IdeaPad Slim 3": [
        "photo-1593642632823-8f785ba67e45",
        "photo-1588872657578-7efd1f1555ed",
        "photo-1603302576837-37561b2e2302"
    ],
    "Aura Smart Phone": [
        "photo-1511707171634-5f897ff02aa9",
        "photo-1598327105666-5b89351aff97",
        "photo-1565849906461-096573c7a8e4"
    ],
    "Nova Laptop Pro": [
        "photo-1603302576837-37561b2e2302",
        "photo-1588872657578-7efd1f1555ed",
        "photo-1496181130204-755241544e35"
    ],
    "Pulse Wireless Earbuds": [
        "photo-1590658268037-6bf12165a8df",
        "photo-1606220588913-b3aacb4d2f46",
        "photo-1588449668365-d15e397f6787"
    ],
    "Orbit Smart Watch": [
        "photo-1508685096489-7aacd43bd3b1",
        "photo-1579586337278-3befd40fd17a",
        "photo-1434494878577-86c23bcb06b9"
    ],
    "Crest 4K Television": [
        "photo-1593305841991-05c297ba4575",
        "photo-1593789381229-26879815b69a",
        "photo-1461151304267-38535e780c79"
    ],
    "Lumen Bluetooth Speaker": [
        "photo-1608043152269-423dbba4e7e1",
        "photo-1589003077984-894e133dabab",
        "photo-1545454675-3531b543be5d"
    ],
    "Atlas Gaming Headset": [
        "photo-1606144042614-b2417e99c4e3",
        "photo-1612287230202-1bf1d85d1bdf",
        "photo-1600861195091-690c92f1d2cc"
    ],
    "Flex Running Shoes": [
        "photo-1542291026-7eec264c27ff",
        "photo-1608231387042-66d1773070a5",
        "photo-1595950653106-6c9ebd614d3a"
    ],
    "Sora Denim Jacket": [
        "photo-1576995853123-5a10305d93c0",
        "photo-1611312449412-6cefac5dc3e4",
        "photo-1516257984-b1b4d707412e"
    ],
    "Mira Cotton Kurti": [
        "photo-1610030469983-98e550d6193c",
        "photo-1608748010899-18f300247112",
        "photo-1617627143750-d86bc21e42bb"
    ],
    "Vega Formal Shirt": [
        "photo-1596755094514-f87e34085b2c",
        "photo-1620012253295-c05518e99309",
        "photo-1602810318383-e386cc2a3ccf"
    ],
    "Echo Leather Belt": [
        "photo-1553062407-98eeb64c6a62",
        "photo-1524388654760-1890dd5d4458",
        "photo-1485968579580-b6d095142e6e"
    ],
    "Chic Tote Bag": [
        "photo-1544816155-12df9643f363",
        "photo-1590874103328-eac38a683ce7",
        "photo-1594223274512-ad4803739b7c"
    ],
    "Oven Fresh Coffee Maker": [
        "photo-1495474472287-4d71bcdd2085",
        "photo-1544787219-7f47ccb76574",
        "photo-1509042239860-f550ce710b93"
    ],
    "Glow Blender": [
        "photo-1578643463396-0997cb5328c1",
        "photo-1553530666-ba11a7da3888",
        "photo-1553530666-ba11a7da3888"
    ],
    "Harbor Microwave Oven": [
        "photo-1574269909862-7e1d70bb8078",
        "photo-1584269600464-37b1b58a9fe7",
        "photo-1626806787461-102c1bfaaea1"
    ],
    "Stoneware Dinner Set": [
        "photo-1610701596007-11502861dcfa",
        "photo-1588854337236-6889d631faa8",
        "photo-1535401991746-da3d9055713e"
    ],
    "Aero Vacuum Cleaner": [
        "photo-1558317374-067fb5f30001",
        "photo-1551830820-330a71b99659",
        "photo-1527515637462-cff94eecc1ac"
    ],
    "PureGlow Face Serum": [
        "photo-1608248597279-f99d160bfcbc",
        "photo-1620916566398-39f1143ab7be",
        "photo-1612817288484-6f916006741a"
    ],
    "SilkCare Shampoo": [
        "photo-1535585209827-a15fcdbc4c2d",
        "photo-1526947425960-945c6e72858f",
        "photo-1608248597279-f99d160bfcbc"
    ],
    "Velvet Moisturizer": [
        "photo-1601049541289-9b1b7bbbfe19",
        "photo-1608248597279-f99d160bfcbc",
        "photo-1556229010-aa3f7ff66b24"
    ],
    "FitPulse Resistance Band": [
        "photo-1517838277536-f5f99be501cd",
        "photo-1518310383802-640c2de311b2",
        "photo-1599447421416-3414500d18a5"
    ],
    "Sprint Yoga Mat": [
        "photo-1601925260368-ae2f83cf8b7f",
        "photo-1592432678016-e910b452f9a2",
        "photo-1599447421416-3414500d18a5"
    ],
    "Peak Water Bottle": [
        "photo-1602143407151-7111542de6e8",
        "photo-1523362628745-0c100150b504",
        "photo-1523362628745-0c100150b504"
    ],
    "Daily Fresh Olive Oil": [
        "photo-1474979266404-7eaacbcd87c5",
        "photo-1471193945509-9ad0617afabf",
        "photo-1541256996761-85df2efaa164"
    ],
    "Nova 12 Pro": [
        "photo-1598327105666-5b89351aff97",
        "photo-1511707171634-5f897ff02aa9",
        "photo-1598327105666-5b89351aff97"
    ],
    "Pixel Lite 5G": [
        "photo-1580910051074-3eb694886505",
        "photo-1598327105666-5b89351aff97",
        "photo-1511707171634-5f897ff02aa9"
    ],
    "Urban Hoodie": [
        "photo-1556821840-3a63f95609a7",
        "photo-1556905055-8f358a7a47b2",
        "photo-1620799140408-edc6dcb6d633"
    ],
    "Satin Party Dress": [
        "photo-1595777457583-95e059d581b8",
        "photo-1566174053879-31528523f8ae",
        "photo-1612336307429-8a898d10e223"
    ],
    "Aura Smart Watch": [
        "photo-1579586337278-3befd40fd17a",
        "photo-1434494878577-86c23bcb06b9",
        "photo-1508685096489-7aacd43bd3b1"
    ],
    "Pulse Bluetooth Speaker": [
        "photo-1589003077984-894e133dabab",
        "photo-1545454675-3531b543be5d",
        "photo-1608043152269-423dbba4e7e1"
    ],
    "Fresh Farm Milk": [
        "photo-1563636619-e9143da7973b",
        "photo-1550583724-b2692b85b150",
        "photo-1563636619-e9143da7973b"
    ],
    "Organic Green Tea": [
        "photo-1597481499750-3e6b22637e12",
        "photo-1597481499750-3e6b22637e12",
        "photo-1576092768241-dec231879fc3"
    ],
    "Glow Face Serum": [
        "photo-1620916566398-39f1143ab7be",
        "photo-1608248597279-f99d160bfcbc",
        "photo-1612817288484-6f916006741a"
    ],
    "Pro Yoga Mat": [
        "photo-1592432678016-e910b452f9a2",
        "photo-1601925260368-ae2f83cf8b7f",
        "photo-1599447421416-3414500d18a5"
    ],
    "Sprint Running Shoes": [
        "photo-1608231387042-66d1773070a5",
        "photo-1542291026-7eec264c27ff",
        "photo-1595950653106-6c9ebd614d3a"
    ],
    "UltraHD Action Camera": [
        "photo-1526170375885-4d8ecf77b99f",
        "photo-1526170375885-4d8ecf77b99f",
        "photo-1516035069371-29a1b244cc32"
    ],
    "Ergonomic Office Chair": [
        "photo-1505797149-43b0069ec26b",
        "photo-1580481072645-022f9a6dbf27",
        "photo-1592078615290-033ee584e267"
    ],
    "Smart Coffee Mug": [
        "photo-1514432324607-a09d9b4aefdd",
        "photo-1509042239860-f550ce710b93",
        "photo-1514432324607-a09d9b4aefdd"
    ],
    "Noise Cancelling Earplugs": [
        "photo-1590658268037-6bf12165a8df",
        "photo-1606220588913-b3aacb4d2f46",
        "photo-1588449668365-d15e397f6787"
    ],
    "Portable Charger 20000mAh": [
        "photo-1625766763788-95dcce9bf5ac",
        "photo-1625766763788-95dcce9bf5ac",
        "photo-1601445638532-3c6f6c3aa1d6"
    ],
    "Leather Passport Holder": [
        "photo-1590874103328-eac38a683ce7",
        "photo-1614162692292-7ac56d7f7f1e",
        "photo-1614162692292-7ac56d7f7f1e"
    ],
    "Stainless Steel Lunch Box": [
        "photo-1534422298391-e4f8c172dddb",
        "photo-1606787366850-de6330128bfc",
        "photo-1534422298391-e4f8c172dddb"
    ],
    "Organic Honey (500g)": [
        "photo-1587049352846-4a222e784d38",
        "photo-1558961363-fa8fdf82db35",
        "photo-1558961363-fa8fdf82db35"
    ],
    "Detox Green Juice": [
        "photo-1540420773420-3366772f4999",
        "photo-1540189549336-e6e99c3679fe",
        "photo-1506084868230-bb9d95c24759"
    ],
    "Aromatherapy Diffuser": [
        "photo-1608571423902-eed4a5ad8108",
        "photo-1602928321679-560bb453f190",
        "photo-1519710164239-da123dc03ef4"
    ],
    "Organic Fresh Vegetables": [
        "photo-1566385101042-1a0aa0c1268c",
        "photo-1543076447-215ad9ba6923",
        "photo-1597362925123-77861d3fbac7"
    ]
}

def download_image(photo_id, product_name, index=0):
    folder = "products"
    safe_name = product_name.lower().replace(' ', '_').replace('-', '_').replace('&', 'and')
    suffix = f"_{index}" if index > 0 else ""
    filename = f"photos/{folder}/{safe_name}{suffix}.jpg"
    target_path = Path(settings.MEDIA_ROOT) / filename
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    url = f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=600&h=600&q=80"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(target_path, 'wb') as f:
                f.write(response.read())
        print(f"Downloaded '{product_name}' (Image {index}) successfully.")
        return filename
    except Exception as e:
        print(f"Failed to download '{product_name}' (Image {index}): {e}")
        return None

def main():
    print("=== STARTING 10 NEW PRODUCTS SEEDING ===")
    
    # 0. Check and rename "Watermelon" if it exists to "Organic Fresh Vegetables"
    watermelon_prod = Product.objects.filter(product_name__iexact="Watermelon").first()
    if not watermelon_prod:
        watermelon_prod = Product.objects.filter(slug="watermelon").first()
    if watermelon_prod:
        print(f"Renaming existing product '{watermelon_prod.product_name}' to 'Organic Fresh Vegetables'")
        watermelon_prod.product_name = "Organic Fresh Vegetables"
        watermelon_prod.slug = "organic-fresh-vegetables"
        watermelon_prod.description = "Fresh and organic mixed vegetables, packed with nutrients and harvested daily."
        watermelon_prod.price = 199.00
        watermelon_prod.original_price = 249.00
        groceries_cat = Category.objects.filter(category_name__iexact="Groceries").first()
        if groceries_cat:
            watermelon_prod.category = groceries_cat
        watermelon_prod.save()
    
    # 1. Create the new default products in the database
    for p_info in NEW_PRODUCTS:
        # Get category
        cat_name = p_info["category_name"]
        category = Category.objects.filter(category_name__iexact=cat_name).first()
        if not category:
            category = Category.objects.create(
                category_name=cat_name,
                slug=slugify(cat_name)
            )
            
        product, created = Product.objects.get_or_create(
            slug=slugify(p_info["name"]),
            defaults={
                "product_name": p_info["name"],
                "price": p_info["price"],
                "original_price": p_info["original_price"],
                "stock": p_info["stock"],
                "description": p_info["description"],
                "is_available": True,
                "category": category,
            }
        )
        if not created:
            product.price = p_info["price"]
            product.original_price = p_info["original_price"]
            product.stock = p_info["stock"]
            product.description = p_info["description"]
            product.category = category
            product.save()
            print(f"Updated product: {p_info['name']}")
        else:
            print(f"Created product: {p_info['name']}")
            
    print("=== SEEDING MULTIPLE IMAGES FOR ALL 52 PRODUCTS ===")
    
    products = Product.objects.all()
    for p in products:
        name = p.product_name
        photo_ids = PRODUCT_UNSPLASH_SETS.get(name)
        if not photo_ids:
            # Fallback photo set if not explicitly listed
            photo_ids = ["photo-1523275335684-37898b6baf30", "photo-1526170375885-4d8ecf77b99f", "photo-1517256064527-09c53b2d0bc6"]
            
        print(f"Processing images for '{name}'...")
        
        # 1. Download and set main product image (index 0)
        main_filename = download_image(photo_ids[0], name, index=0)
        if main_filename:
            p.images = main_filename
            p.save()
            
        # 2. Clear old extra images to avoid duplicates on re-run
        ProductImage.objects.filter(product=p).delete()
        
        # 3. Download and register extra images (indices 1 and 2)
        for i in range(1, len(photo_ids)):
            extra_filename = download_image(photo_ids[i], name, index=i)
            if extra_filename:
                ProductImage.objects.create(
                    product=p,
                    image=extra_filename,
                    caption=f"{name} Detail view {i}"
                )
                
    print("=== COMPLETED ALL SEEDING AND MULTIPLE IMAGE WORK ===")

if __name__ == '__main__':
    main()
