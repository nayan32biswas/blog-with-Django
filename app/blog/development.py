import warnings

from .settings import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
SESSION_COOKIE_SECURE = True


INSTALLED_APPS += ["drf_spectacular"]

SPECTACULAR_SETTINGS = {
    "TITLE": "Django Blog API",
    "DESCRIPTION": "Django Blog API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1",
    # OTHER SETTINGS
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
}
# REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
#     "rest_framework_simplejwt.authentication.JWTAuthentication",
#     "rest_framework.authentication.SessionAuthentication",
#     "rest_framework.authentication.TokenAuthentication",
# )
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"


try:
    __import__("debug_toolbar")
except ImportError as exc:
    warnings.warn(f"{exc} -- Install the missing dependencies ")
else:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = type(str("c"), (), {"__contains__": lambda *a: True})()

try:
    pass
except ImportError:
    pass
