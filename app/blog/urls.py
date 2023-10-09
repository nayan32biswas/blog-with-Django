"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import logging

from base import views as base_views
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from post import views as post_views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from user import views as user_views

logger = logging.getLogger(__name__)

router = DefaultRouter()

router.register(r"users", user_views.UserListViewSet, basename="users")
router.register(r"posts", post_views.PostViewSet, basename="post")
router.register(
    r"posts/(?P<slug>[^/.]+)/comments", post_views.CommentViewSet, basename="post"
)

urlpatterns = [
    path("", base_views.BaseViewSet.as_view({"get": "home"}), name="Home"),
    path("admin/", admin.site.urls),
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/v1/update-access-token/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path(
        "api/v1/registration/",
        user_views.RegistrationAPIView.as_view(),
        name="registration",
    ),
    path(
        "api/v1/change-password/",
        user_views.PasswordViewSet.as_view({"post": "password_reset"}),
        name="me",
    ),
    path("api/v1/me/", user_views.UserViewSet.as_view(), name="me"),
    path("api/v1/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += [
        # YOUR PATTERNS
        path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
        # Optional UI:
        path(
            "api/v1/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/v1/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]

if settings.DEBUG is True:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    try:
        import debug_toolbar
    except ImportError:
        logger.warning("The debug toolbar was not installed.")
    else:
        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
