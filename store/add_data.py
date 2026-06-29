import os
import urllib.request
import urllib.parse
from pathlib import Path
import django

# Initialize Django setup so the script can interact with the database
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniMart.settings')
django.setup()

from store.models import Category, Product
from django.conf import settings

PLACEHOLDER_IMAGES = {
    'products': [
        'photos/products/placeholder.jpg',
        'photos/products/default.jpg',
        'photos/products/new_default.jpg',
    ],
    'categories': [
        'photos/categories/placeholder.jpg',
        'photos/categories/default.jpg',
    ],
}


def download_image(query, filename):
    target_path = Path(settings.MEDIA_ROOT) / filename
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        return target_path

    url = f"https://loremflickr.com/800/600/{urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(target_path, 'wb') as f:
                f.write(response.read())
        print(f"Downloaded image for '{query}' to {filename}")
    except Exception as e:
        print(f"Failed to download image for '{query}': {e}")
    return target_path


def create_data():
    print("Creating categories...")
    categories_data = [
        {
            'category_name': 'Electronics',
            'slug': 'electronics',
            'description': 'Gadgets and electronic devices.',
            'image': Path('photos/categories/electronics.jpg'),
            'image_query': 'electronics',
        },
        {
            'category_name': 'Clothing',
            'slug': 'clothing',
            'description': 'Apparel and fashion.',
            'image': Path('photos/categories/clothing.jpg'),
            'image_query': 'fashion clothing',
        },
        {
            'category_name': 'Home & Kitchen',
            'slug': 'home-kitchen',
            'description': 'Household items and kitchen essentials.',
            'image': Path('photos/categories/home-kitchen.jpg'),
            'image_query': 'home kitchen',
        },
    ]

    category_objects = {}
    for data in categories_data:
        category, _ = Category.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'category_name': data['category_name'],
                'description': data['description'],
            }
        )

        if not category.category_image or category.category_image.name in PLACEHOLDER_IMAGES['categories']:
            download_image(data['image_query'], data['image'])
            category.category_image = str(data['image'])
            category.save()

        category_objects[data['slug']] = category

    products_data = [
        {
            'name': 'Smartphone X',
            'slug': 'smartphone-x',
            'price': 45000.00,
            'stock': 50,
            'category': category_objects['electronics'],
            'image_query': 'smartphone',
        },
        {
            'name': 'Laptop Pro',
            'slug': 'laptop-pro',
            'price': 85000.00,
            'stock': 30,
            'category': category_objects['electronics'],
            'image_query': 'laptop computer',
        },
        {
            'name': 'Wireless Earbuds',
            'slug': 'wireless-earbuds',
            'price': 2500.00,
            'stock': 100,
            'category': category_objects['electronics'],
            'image_query': 'wireless earbuds',
        },
        {
            'name': 'Smart Watch',
            'slug': 'smart-watch',
            'price': 5000.00,
            'stock': 70,
            'category': category_objects['electronics'],
            'image_query': 'smart watch',
        },
        {
            'name': '4K TV',
            'slug': '4k-tv',
            'price': 35000.00,
            'stock': 20,
            'category': category_objects['electronics'],
            'image_query': '4k television',
        },
        {
            'name': 'Gaming Console',
            'slug': 'gaming-console',
            'price': 40000.00,
            'stock': 15,
            'category': category_objects['electronics'],
            'image_query': 'gaming console',
        },
        {
            'name': 'Bluetooth Speaker',
            'slug': 'bluetooth-speaker',
            'price': 1500.00,
            'stock': 80,
            'category': category_objects['electronics'],
            'image_query': 'bluetooth speaker',
        },
        {
            'name': 'Tablet',
            'slug': 'tablet',
            'price': 20000.00,
            'stock': 40,
            'category': category_objects['electronics'],
            'image_query': 'tablet computer',
        },
        {
            'name': "Men's T-Shirt",
            'slug': 'mens-tshirt',
            'price': 500.00,
            'stock': 200,
            'category': category_objects['clothing'],
            'image_query': 'men t-shirt',
        },
        {
            'name': "Women's Jeans",
            'slug': 'womens-jeans',
            'price': 1200.00,
            'stock': 150,
            'category': category_objects['clothing'],
            'image_query': 'women jeans',
        },
        {
            'name': 'Running Shoes',
            'slug': 'running-shoes',
            'price': 2500.00,
            'stock': 90,
            'category': category_objects['clothing'],
            'image_query': 'running shoes',
        },
        {
            'name': 'Winter Jacket',
            'slug': 'winter-jacket',
            'price': 3000.00,
            'stock': 60,
            'category': category_objects['clothing'],
            'image_query': 'winter jacket',
        },
        {
            'name': 'Cotton Kurta',
            'slug': 'cotton-kurta',
            'price': 800.00,
            'stock': 120,
            'category': category_objects['clothing'],
            'image_query': 'cotton kurta',
        },
        {
            'name': 'Formal Shirt',
            'slug': 'formal-shirt',
            'price': 1000.00,
            'stock': 100,
            'category': category_objects['clothing'],
            'image_query': 'formal shirt',
        },
        {
            'name': 'Leather Belt',
            'slug': 'leather-belt',
            'price': 400.00,
            'stock': 300,
            'category': category_objects['clothing'],
            'image_query': 'leather belt',
        },
        {
            'name': 'Coffee Maker',
            'slug': 'coffee-maker',
            'price': 2000.00,
            'stock': 50,
            'category': category_objects['home-kitchen'],
            'image_query': 'coffee maker',
        },
        {
            'name': 'Blender',
            'slug': 'blender',
            'price': 1500.00,
            'stock': 60,
            'category': category_objects['home-kitchen'],
            'image_query': 'blender',
        },
        {
            'name': 'Microwave Oven',
            'slug': 'microwave-oven',
            'price': 8000.00,
            'stock': 25,
            'category': category_objects['home-kitchen'],
            'image_query': 'microwave oven',
        },
        {
            'name': 'Non-Stick Pan',
            'slug': 'non-stick-pan',
            'price': 800.00,
            'stock': 120,
            'category': category_objects['home-kitchen'],
            'image_query': 'non-stick pan',
        },
        {
            'name': 'Water Purifier',
            'slug': 'water-purifier',
            'price': 12000.00,
            'stock': 30,
            'category': category_objects['home-kitchen'],
            'image_query': 'water purifier',
        },
        {
            'name': 'Vacuum Cleaner',
            'slug': 'vacuum-cleaner',
            'price': 5000.00,
            'stock': 40,
            'category': category_objects['home-kitchen'],
            'image_query': 'vacuum cleaner',
        },
        {
            'name': 'Dinner Set',
            'slug': 'dinner-set',
            'price': 2500.00,
            'stock': 80,
            'category': category_objects['home-kitchen'],
            'image_query': 'dinner set',
        },
    ]

    print("Adding 22 products...")
    for item in products_data:
        image_path = Path('photos/products') / f"{item['slug']}.jpg"
        download_image(item['image_query'], image_path)

        product, created = Product.objects.get_or_create(
            slug=item['slug'],
            defaults={
                'product_name': item['name'],
                'price': item['price'],
                'stock': item['stock'],
                'is_available': True,
                'category': item['category'],
                'description': f"This is a high-quality {item['name']}.",
                'images': str(image_path),
            }
        )

        if not created and (not product.images.name or product.images.name in PLACEHOLDER_IMAGES['products']):
            product.images = str(image_path)
            product.save()

    print('Data seeding completed. Product and category images are now set to category- and product-specific images.')


if __name__ == '__main__':
    create_data()
