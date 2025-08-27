from django.utils import translation
from django.conf import settings

class APILanguageMiddleware:
    """
    Middleware for API requests that activates language based on:
    1. Query parameter ?lang=
    2. HTTP header Accept-Language
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1️⃣ Check "lang" query parameter
        lang_code = request.GET.get("lang")

        # 2️⃣ If query param is missing, check "Accept-Language" header
        if not lang_code:
            lang_header = request.META.get("HTTP_ACCEPT_LANGUAGE")
            if lang_header:
                # Take only the first segment before a comma
                lang_code = lang_header.split(",")[0].split("-")[0]

        # 3️⃣ Validate language code
        if lang_code and lang_code in dict(settings.LANGUAGES):
            translation.activate(lang_code)
            request.LANGUAGE_CODE = lang_code
        else:
            # Fallback to default language
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE

        response = self.get_response(request)

        # Optional: set "Content-Language" header in response
        response["Content-Language"] = request.LANGUAGE_CODE
        return response
