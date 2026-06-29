from django.shortcuts import render
from adminpanel.models import SystemSettings

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Fetch system settings (retrieve or create row ID 1)
        settings_obj, _ = SystemSettings.objects.get_or_create(id=1)
        
        # Check if maintenance mode is enabled
        if settings_obj.maintenance_mode:
            # Bypass checks:
            # - Admin/Staff users (so they can log in, navigate, and turn it off)
            # - Admin URLs starting with '/panel/' or '/admin/'
            # - Authentication URL endpoints
            path = request.path
            
            if request.user.is_authenticated and request.user.is_staff:
                return self.get_response(request)
                
            if path.startswith('/panel/') or path.startswith('/admin/') or 'login' in path or 'logout' in path:
                return self.get_response(request)
                
            # Render the beautiful maintenance page
            return render(request, 'store/maintenance.html', status=503)

        return self.get_response(request)
