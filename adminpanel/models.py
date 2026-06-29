from django.db import models

class SystemSettings(models.Model):
    store_name = models.CharField(max_length=100, default='MiniMart')
    contact_email = models.EmailField(default='admin@minimart.com')
    support_phone = models.CharField(max_length=20, default='+1-234-567-890')
    maintenance_mode = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'
        
    def __str__(self):
        return "System Settings"

