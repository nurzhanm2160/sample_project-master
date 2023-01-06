from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .yasg import urlpatterns as swagger_url

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

admin_url = settings.ADMIN_URL

schema_view = get_schema_view(
    openapi.Info(
        title="Project API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.ourapp.com/policies/terms/",
        contact=openapi.Contact(email="contact@expenses.local"),
        license=openapi.License(name="Test License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('coin/', include('coin.urls')),
    path(f'{admin_url}/', admin.site.urls),
    path(f'{admin_url}/defender/', include('defender.urls')),
    path('api/', include('rest_framework.urls')),
    path('rosetta/', include('rosetta.urls')),
    path('', schema_view.with_ui('swagger',
                                 cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
                                       cache_timeout=0), name='schema-redoc'),
]

urlpatterns += swagger_url

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    if settings.ENABLE_SILK:
        urlpatterns.append(path('silk/', include('silk.urls', namespace='silk')))
    if settings.ENABLE_DEBUG_TOOLBAR:
        urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
