from django.conf import settings
from django.contrib import admin
from django.urls import path
from djoser.views import UserViewSet
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from users.views import OtpActivateView, OtpObtainView, OtpUserViewSet, TokensObtainWithOtp

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/user/', OtpUserViewSet.as_view({'post': 'create'})),
    path('api/v1/auth/user/activation/', OtpActivateView.as_view()),
    path('api/v1/auth/user/otp/', OtpObtainView.as_view()),
    path('api/v1/auth/user/me/', UserViewSet.as_view({'get': 'me', 'patch': 'me', 'delete': 'me'})),
    path('api/v1/auth/jwt/create/', TokensObtainWithOtp.as_view()),
    path('api/v1/auth/jwt/refresh/', TokenRefreshView.as_view()),
    path('api/v1/auth/jwt/verify/', TokenVerifyView.as_view()),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title='Longevity InTime Test Backend Task API',
            default_version='1',
            description=('API description for Longevity InTime Test Backend Task'),
        ),
        public=True,
    )

    urlpatterns += [
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
    ]
