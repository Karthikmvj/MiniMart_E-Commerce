from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        from django.utils.translation import trans_real, _trans
        original_gettext = trans_real.gettext
        
        def custom_gettext(message):
            if not message:
                return message
            lang = trans_real.get_language()
            if lang == 'ta':
                from .translations import TAMIL_TRANSLATIONS
                translated = TAMIL_TRANSLATIONS.get(message)
                if translated:
                    return translated
            return original_gettext(message)
            
        trans_real.gettext = custom_gettext
        
        # Override on the dynamic _trans proxy wrapper to bypass caching issues
        if hasattr(_trans, 'gettext'):
            setattr(_trans, 'gettext', custom_gettext)
        if 'gettext' in _trans.__dict__:
            _trans.__dict__['gettext'] = custom_gettext
