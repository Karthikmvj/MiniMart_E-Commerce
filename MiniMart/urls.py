from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # Django i18n URL for language switching
    path('i18n/', include('django.conf.urls.i18n')),
]

# URLs that should be translated
urlpatterns += i18n_patterns(
    path('accounts/', include('accounts.urls')),
    path('panel/', include('adminpanel.urls')),
    path('', include('store.urls')),
    prefix_default_language=False
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)