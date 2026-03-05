import uuid
import hmac
import hashlib
from django.conf import settings


def hash_token(raw_token: str) -> str:
    """
    Takes a raw UUID string and returns an HMAC-SHA256 hash.
    This is what gets stored in the database.
    """
    return hmac.new(
        settings.HMAC_SECRET.encode(),
        raw_token.encode(),
        hashlib.sha256
    ).hexdigest()


class AnonymousSessionMiddleware:
    """
    Runs on every request, before any view is called.

    - Checks for our custom cookie
    - If missing: generates a new UUID, sets the cookie
    - Always attaches the hashed token to request.session_token
      so any view can access it as request.session_token
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        raw_token = request.COOKIES.get('anon_token')

        if not raw_token:
            raw_token = str(uuid.uuid4())
            request._set_anon_cookie = raw_token  # flag to set cookie later

        request.session_token = hash_token(raw_token)

        response = self.get_response(request)

        if hasattr(request, '_set_anon_cookie'):
            response.set_cookie(
                'anon_token',
                request._set_anon_cookie,
                max_age=60 * 60 * 24 * 365,  # 1 year
                httponly=True,                 # JS cannot read this cookie
                samesite='Lax',
            )

        return response