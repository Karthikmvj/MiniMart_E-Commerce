import os
import random
from pathlib import Path
import requests

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniMart.settings')
django.setup()

from PIL import Image, ImageDraw, ImageFilter

from store.models import Category, Product

BASE_DIR = Path(__file__).resolve().parent.parent
CATEGORY_DIR = BASE_DIR / 'media' / 'photos' / 'categories'
PRODUCT_DIR = BASE_DIR / 'media' / 'photos' / 'products'

CATEGORY_DIR.mkdir(parents=True, exist_ok=True)
PRODUCT_DIR.mkdir(parents=True, exist_ok=True)


def create_placeholder_image(target_dir: Path, name: str, color_a: str, color_b: str, label: str, keyword: str = None) -> str:
    """Download a real image based on a keyword or create a placeholder if it fails, returning its relative media path."""
    file_name = f"{name.lower().replace(' ', '-').replace('&', 'and')[:80]}.jpg"
    file_path = target_dir / file_name
    
    if keyword:
        url = f"https://loremflickr.com/800/600/{keyword}"
    else:
        # Create a consistent seed based on the name
        seed = name.lower().replace(' ', '').replace('&', 'and')
        url = f"https://picsum.photos/seed/{seed}/800/600"
    
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        # Verify and format image
        img = Image.open(file_path)
        img = img.convert('RGB')
        img.save(file_path, format='JPEG')
        
        return file_path.relative_to(BASE_DIR / 'media').as_posix().replace('\\', '/')
    except requests.exceptions.RequestException as e:
        print(f"Failed to download real image for {name} from {url}: {e}. Falling back to placeholder.")

    # Fallback to generated image
    image = Image.new('RGB', (800, 600), color_a)
    draw = ImageDraw.Draw(image)

    for i in range(8):
        x0 = random.randint(0, 700)
        y0 = random.randint(0, 500)
        x1 = x0 + random.randint(40, 180)
        y1 = y0 + random.randint(40, 180)
        draw.rectangle([x0, y0, x1, y1], fill=color_b, outline=None)

    image = image.filter(ImageFilter.GaussianBlur(radius=1.2))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([40, 40, 760, 560], radius=30, outline=(255, 255, 255, 80), width=4)
    draw.text((80, 80), label[:18].upper(), fill=(255, 255, 255), spacing=2)
    draw.text((80, 150), name[:24], fill=(255, 255, 255), spacing=2)

    fallback_path = target_dir / f"{name.lower().replace(' ', '-').replace('&', 'and')[:80]}.png"
    image.save(fallback_path, format='PNG')
    return fallback_path.relative_to(BASE_DIR / 'media').as_posix().replace('\\', '/')


def seed_data():
    """Create sample categories and products if they do not already exist."""
    categories = [
        {
            'category_name': 'Mobiles',
            'slug': 'mobiles',
            'description': 'Feature-rich smartphones with premium cameras and fast performance.',
            'keyword': 'mobile phone',
        },
        {
            'category_name': 'Fashion',
            'slug': 'fashion',
            'description': 'Stylish clothing, footwear, and modern accessories with attractive offers.',
            'keyword': 'fashion',
        },
        {
            'category_name': 'Electronics',
            'slug': 'electronics',
            'description': 'Smart devices, audio gear, and everyday tech essentials.',
            'keyword': 'electronics',
        },
        {
            'category_name': 'Groceries',
            'slug': 'groceries',
            'description': 'Fresh staples and pantry favorites for every meal.',
            'keyword': 'groceries',
        },
        {
            'category_name': 'Beauty',
            'slug': 'beauty',
            'description': 'Wellness, skincare, and beauty essentials for daily care.',
            'keyword': 'beauty',
        },
        {
            'category_name': 'Sports',
            'slug': 'sports',
            'description': 'Performance gear and active lifestyle products.',
            'keyword': 'sports',
        },
    ]

    created_categories = {}
    for item in categories:
        category, created = Category.objects.get_or_create(
            slug=item['slug'],
            defaults={
                'category_name': item['category_name'],
                'description': item['description'],
            },
        )
        image_name = str(category.category_image) if category.category_image else ''
        needs_image = created or not image_name or not (BASE_DIR / 'media' / image_name).exists()
        if needs_image:
            image_path = create_placeholder_image(
                CATEGORY_DIR,
                category.category_name,
                color_a=(24, 58, 108),
                color_b=(56, 189, 248),
                label='Category',
                keyword=item.get('keyword'),
            )
            category.category_image = image_path
            category.save()
        created_categories[item['slug']] = category

    beauty_category = created_categories.get('beauty')
    if beauty_category:
        existing_beauty_product = Product.objects.filter(slug='silkcare-shampoo').first()
        if existing_beauty_product and existing_beauty_product.category_id != beauty_category.id:
            existing_beauty_product.category = beauty_category
            existing_beauty_product.save(update_fields=['category'])

    products = [
        {
            'name': 'Nova 12 Pro',
            'slug': 'nova-12-pro',
            'price': 27999,
            'original_price': 32999,
            'stock': 18,
            'category': 'mobiles',
            'keyword': 'smartphone',
            'description': 'A premium 5G smartphone with a bright AMOLED display, fast charging, and excellent camera quality.',
        },
        {
            'name': 'Pixel Lite 5G',
            'slug': 'pixel-lite-5g',
            'price': 24999,
            'original_price': 29999,
            'stock': 14,
            'category': 'mobiles',
            'keyword': 'mobilephone',
            'description': 'Slim and stylish 5G phone with AI camera features, long battery life, and a smooth everyday experience.',
        },
        {
            'name': 'Urban Hoodie',
            'slug': 'urban-hoodie',
            'price': 1599,
            'original_price': 1999,
            'stock': 22,
            'category': 'fashion',
            'keyword': 'hoodie',
            'description': 'A soft and cozy hoodie designed for everyday comfort and a stylish streetwear look.',
        },
        {
            'name': 'Satin Party Dress',
            'slug': 'satin-party-dress',
            'price': 2299,
            'original_price': 2799,
            'stock': 16,
            'category': 'fashion',
            'keyword': 'dress',
            'description': 'Elegant satin dress with a flattering fit that is perfect for parties and special occasions.',
        },
        {
            'name': 'Aura Smart Watch',
            'slug': 'aura-smart-watch',
            'price': 4999,
            'original_price': 5999,
            'stock': 25,
            'category': 'electronics',
            'keyword': 'smartwatch',
            'description': 'Track your fitness, notifications, and wellness goals with this sleek smart watch.',
        },
        {
            'name': 'Pulse Bluetooth Speaker',
            'slug': 'pulse-bluetooth-speaker',
            'price': 1799,
            'original_price': 2299,
            'stock': 35,
            'category': 'electronics',
            'keyword': 'speaker',
            'description': 'Portable speaker with clear sound, deep bass, and long battery backup for travel and home use.',
        },
        {
            'name': 'Fresh Farm Milk',
            'slug': 'fresh-farm-milk',
            'price': 79,
            'original_price': 99,
            'stock': 48,
            'category': 'groceries',
            'keyword': 'milk',
            'description': 'Fresh dairy milk packed with nutrition and perfect for daily breakfasts and beverages.',
        },
        {
            'name': 'Organic Green Tea',
            'slug': 'organic-green-tea',
            'price': 199,
            'original_price': 249,
            'stock': 42,
            'category': 'groceries',
            'keyword': 'tea',
            'description': 'Premium green tea with a refreshing flavor and a healthy everyday routine.',
        },
        {
            'name': 'Glow Face Serum',
            'slug': 'glow-face-serum',
            'price': 899,
            'original_price': 1199,
            'stock': 30,
            'category': 'beauty',
            'keyword': 'serum',
            'description': 'Lightweight serum that hydrates the skin and enhances your natural glow.',
        },
        {
            'name': 'SilkCare Shampoo',
            'slug': 'silkcare-shampoo',
            'price': 499,
            'original_price': 649,
            'stock': 50,
            'category': 'beauty',
            'keyword': 'shampoo',
            'description': 'Gentle shampoo formulated to nourish hair, improve softness, and add shine.',
        },
        {
            'name': 'Pro Yoga Mat',
            'slug': 'pro-yoga-mat',
            'price': 1299,
            'original_price': 1599,
            'stock': 24,
            'category': 'sports',
            'keyword': 'yogamat',
            'description': 'Comfortable and durable yoga mat with excellent grip for exercise and relaxation.',
        },
        {
            'name': 'Sprint Running Shoes',
            'slug': 'sprint-running-shoes',
            'price': 2799,
            'original_price': 3299,
            'stock': 22,
            'category': 'sports',
            'keyword': 'shoes',
            'description': 'Lightweight running shoes built for comfort, balance, and everyday active movement.',
        },
    ]

    for item in products:
        category = created_categories[item['category']]
        product, created = Product.objects.get_or_create(
            slug=item['slug'],
            defaults={
                'product_name': item['name'],
                'description': item['description'],
                'price': item['price'],
                'original_price': item.get('original_price', item['price']),
                'stock': item['stock'],
                'is_available': True,
                'category': category,
            },
        )

        if not created and product.original_price is None:
            product.original_price = item.get('original_price', item['price'])
            product.save(update_fields=['original_price'])

        image_name = str(product.images) if product.images else ''
        needs_image = created or not image_name or not (BASE_DIR / 'media' / image_name).exists()
        if needs_image:
            image_path = create_placeholder_image(
                PRODUCT_DIR,
                product.product_name,
                color_a=(random.randint(10, 80), random.randint(10, 80), random.randint(10, 80)),
                color_b=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                label='Product',
                keyword=item.get('keyword'),
            )
            product.images = image_path
            product.save()

    print(f'Seeded {len(created_categories)} categories and {len(products)} products successfully.')


if __name__ == '__main__':
    seed_data()
