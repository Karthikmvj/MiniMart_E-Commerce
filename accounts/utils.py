from django.shortcuts import redirect
from django.urls import translate_url
from django.views.decorators.http import require_POST
from django.utils import translation

@require_POST
def set_language_and_redirect(request, language_code):
    next_url = request.META.get('HTTP_REFERER', '/')
    translation.activate(language_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = language_code
    return redirect(translate_url(next_url, language_code))