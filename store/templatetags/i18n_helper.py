from django import template
from django.urls import translate_url as django_translate_url
from django.utils.translation import gettext

register = template.Library()

@register.filter
def translate_url(url, lang_code):
    return django_translate_url(url, lang_code)

@register.filter
def translate(text):
    if not text:
        return text
    return gettext(str(text))
