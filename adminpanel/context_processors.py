from store.models import Product
from .models import SystemSettings

def sidebar_stats(request):
    if request.user.is_authenticated and request.user.is_active and request.user.is_staff:
        low_stock_count = Product.objects.filter(stock__lt=10).count()
        return {'low_stock_count': low_stock_count}
    return {'low_stock_count': 0}

def system_settings(request):
    settings_obj, _ = SystemSettings.objects.get_or_create(id=1)
    return {'system_settings': settings_obj}
